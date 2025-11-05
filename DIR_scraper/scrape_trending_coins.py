#!/usr/bin/env python3
"""
🌙 Moon Dev's CoinGecko Trending Coins Scraper 🔥

Scrapes individual coins from trending categories with price, change, market cap, and volume
Outputs everything to ONE CSV table
"""

import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager

# Configuration
START_URL = "https://www.coingecko.com/en/trending-categories"
OUTPUT_FILE = Path("DIR_scraper/trending_coins_data.csv")
MAX_CATEGORIES = 20  # Maximum categories to scrape
MAX_COINS_PER_CATEGORY = 50  # Max coins to get from each category

def setup_driver():
    """Setup Firefox driver with options to avoid detection"""
    print("🔧 Setting up browser driver...")

    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Run in background
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)

    return driver

def get_category_links(driver):
    """Get all category links from trending categories page"""
    print(f"\n🌐 Loading trending categories page...")

    try:
        driver.get(START_URL)

        # Wait for page to load
        print("  ⏳ Waiting for page to load...")
        time.sleep(5)

        # Take a screenshot for debugging
        driver.save_screenshot("DIR_scraper/debug_screenshot.png")
        print("  📸 Screenshot saved to DIR_scraper/debug_screenshot.png")

        # Try multiple selectors
        category_elements = []

        # Try different selectors
        selectors = [
            "tbody tr td:nth-child(2) a",
            "table tbody tr a",
            "a[href*='/categories/']",
            ".coin-table tbody tr a",
        ]

        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  ✓ Found {len(elements)} elements with selector: {selector}")
                    category_elements = elements
                    break
            except:
                continue

        if not category_elements:
            # Save page source for debugging
            with open("DIR_scraper/debug_page_source.html", "w") as f:
                f.write(driver.page_source)
            print("  📄 Page source saved to DIR_scraper/debug_page_source.html")
            print("  ⚠️ No category elements found with any selector")

        categories = []
        for elem in category_elements[:MAX_CATEGORIES]:
            try:
                name = elem.text.strip()
                url = elem.get_attribute("href")

                # Filter for category links
                if url and '/categories/' in url and name:
                    categories.append({
                        'name': name,
                        'url': url
                    })
                    print(f"  ✓ Found category: {name}")
            except:
                continue

        print(f"\n📊 Found {len(categories)} trending categories")
        return categories

    except Exception as e:
        print(f"❌ Error getting categories: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def scrape_coins_from_category(driver, category_name, category_url):
    """Scrape individual coins from a category page"""
    print(f"\n🔍 Scraping coins from: {category_name}")

    try:
        driver.get(category_url)

        # Wait for coin table
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
        )

        time.sleep(2)

        # Find all coin rows
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")[:MAX_COINS_PER_CATEGORY]

        coins = []

        for idx, row in enumerate(rows, 1):
            try:
                # Get all cells
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) < 5:
                    continue

                # Extract coin rank/number (first cell)
                try:
                    rank = cells[0].text.strip()
                except:
                    rank = str(idx)

                # Extract coin name and symbol (usually in cells[2])
                try:
                    name_cell = cells[2]
                    coin_link = name_cell.find_element(By.CSS_SELECTOR, "a")
                    coin_name = coin_link.text.strip().split('\n')[0]  # Get first line
                    coin_url = coin_link.get_attribute("href")
                    coin_id = coin_url.split('/')[-1] if coin_url else ""

                    # Try to get symbol
                    try:
                        symbol_elem = name_cell.find_element(By.CSS_SELECTOR, ".tw-text-gray-500")
                        symbol = symbol_elem.text.strip()
                    except:
                        # Sometimes symbol is in the text
                        full_text = name_cell.text.strip()
                        lines = full_text.split('\n')
                        symbol = lines[1] if len(lines) > 1 else ""
                except Exception as e:
                    print(f"    ⚠️ Error parsing name/symbol: {str(e)}")
                    continue

                # Extract price (usually cells[3])
                try:
                    price = cells[3].text.strip().replace('$', '').replace(',', '')
                except:
                    price = "N/A"

                # Extract 24h change (usually cells[4] or cells[5])
                price_change_24h = "N/A"
                for cell_idx in [4, 5]:
                    try:
                        text = cells[cell_idx].text.strip()
                        if '%' in text:
                            price_change_24h = text
                            break
                    except:
                        continue

                # Extract volume 24h (look for large numbers)
                volume_24h = "N/A"
                for cell_idx in range(5, min(len(cells), 8)):
                    try:
                        text = cells[cell_idx].text.strip()
                        if '$' in text and 'M' in text or 'B' in text or 'K' in text:
                            if volume_24h == "N/A" or cell_idx == 5:
                                volume_24h = text
                    except:
                        continue

                # Extract market cap (look for large numbers)
                market_cap = "N/A"
                for cell_idx in range(6, min(len(cells), 9)):
                    try:
                        text = cells[cell_idx].text.strip()
                        if '$' in text and ('M' in text or 'B' in text or 'K' in text):
                            if market_cap == "N/A":
                                market_cap = text
                    except:
                        continue

                coin_data = {
                    'rank': rank,
                    'coin_id': coin_id,
                    'coin_name': coin_name,
                    'symbol': symbol,
                    'price': price,
                    'price_change_24h': price_change_24h,
                    'volume_24h': volume_24h,
                    'market_cap': market_cap,
                    'category': category_name,
                    'scraped_at': datetime.now().isoformat()
                }

                coins.append(coin_data)
                print(f"  ✓ {idx}. {coin_name} ({symbol}) - Price: {price}, Change: {price_change_24h}")

            except Exception as e:
                print(f"  ✗ Error parsing row {idx}: {str(e)}")
                continue

        print(f"  📊 Extracted {len(coins)} coins from {category_name}")
        return coins

    except Exception as e:
        print(f"  ❌ Error scraping category: {str(e)}")
        return []

def main():
    """Main scraper function"""
    print("🌙 Moon Dev's CoinGecko Trending Coins Scraper 🚀")
    print(f"⚙️ Configuration:")
    print(f"  • Output File: {OUTPUT_FILE.absolute()}")
    print(f"  • Max Categories: {MAX_CATEGORIES}")
    print(f"  • Max Coins per Category: {MAX_COINS_PER_CATEGORY}")

    driver = None
    all_coins = []

    try:
        driver = setup_driver()

        # Get all category links
        categories = get_category_links(driver)

        if not categories:
            print("❌ No categories found!")
            return

        # Scrape coins from each category
        for idx, category in enumerate(categories, 1):
            print(f"\n{'='*60}")
            print(f"Category {idx}/{len(categories)}")

            coins = scrape_coins_from_category(
                driver,
                category['name'],
                category['url']
            )

            all_coins.extend(coins)

            # Rate limiting
            time.sleep(3)

            # Progress update
            print(f"\n📈 Total coins collected so far: {len(all_coins)}")

        # Save to CSV
        if all_coins:
            df = pd.DataFrame(all_coins)

            # Remove duplicates based on coin_id
            df = df.drop_duplicates(subset=['coin_id'], keep='first')

            # Create output directory
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Save to CSV
            df.to_csv(OUTPUT_FILE, index=False)

            print(f"\n{'='*60}")
            print(f"✨ Scraping Complete!")
            print(f"📊 Total unique coins: {len(df)}")
            print(f"💾 Saved to: {OUTPUT_FILE.absolute()}")

            # Show summary statistics
            print(f"\n📈 Summary:")
            print(f"  • Total categories scraped: {len(categories)}")
            print(f"  • Total coins collected: {len(all_coins)}")
            print(f"  • Unique coins: {len(df)}")
            print(f"  • Coins with price data: {df['price'].ne('N/A').sum()}")
            print(f"  • Coins with 24h change: {df['price_change_24h'].ne('N/A').sum()}")
            print(f"  • Coins with volume data: {df['volume_24h'].ne('N/A').sum()}")
            print(f"  • Coins with market cap: {df['market_cap'].ne('N/A').sum()}")

            # Show top 10 by category
            print(f"\n🔥 Sample of collected coins:")
            for _, row in df.head(10).iterrows():
                print(f"  • {row['coin_name']:20s} ({row['symbol']:6s}) - ${row['price']:>12s} | {row['price_change_24h']:>8s} | Cap: {row['market_cap']:>12s}")

        else:
            print("\n❌ No coins collected!")

    except KeyboardInterrupt:
        print("\n👋 Scraping cancelled by user")
        # Save whatever we have so far
        if all_coins:
            df = pd.DataFrame(all_coins)
            df = df.drop_duplicates(subset=['coin_id'], keep='first')
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"💾 Saved {len(df)} coins to: {OUTPUT_FILE.absolute()}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("\n🔒 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    main()

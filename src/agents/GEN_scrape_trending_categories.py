#!/usr/bin/env python3
"""
🌙 Moon Dev's CoinGecko Trending Categories Scraper 🔥

Scrapes trending categories from CoinGecko with automatic pagination
"""

import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
START_URL = "https://www.coingecko.com/en/trending-categories"
OUTPUT_FILE = Path("src/data/trending_categories_coins.csv")
MAX_PAGES = 10  # Maximum pages to scrape

def setup_driver():
    """Setup Chrome driver with options to avoid detection"""
    print("🔧 Setting up browser driver...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_page(driver, page_num):
    """Scrape trending categories from current page"""
    print(f"\n📄 Scraping page {page_num}...")

    try:
        # Wait for the main content to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )

        time.sleep(2)  # Let JavaScript render

        # Find all rows in the table
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"  Found {len(rows)} categories on this page")

        categories_data = []

        for idx, row in enumerate(rows, 1):
            try:
                # Extract category name and link
                category_link = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) a")
                category_name = category_link.text.strip()
                category_url = category_link.get_attribute("href")

                # Extract market cap (if available)
                try:
                    market_cap_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(3)")
                    market_cap_text = market_cap_elem.text.strip()
                except:
                    market_cap_text = "N/A"

                # Extract 24h change (if available)
                try:
                    change_24h_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)")
                    change_24h_text = change_24h_elem.text.strip()
                except:
                    change_24h_text = "N/A"

                # Extract volume 24h (if available)
                try:
                    volume_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)")
                    volume_text = volume_elem.text.strip()
                except:
                    volume_text = "N/A"

                category_data = {
                    'rank': (page_num - 1) * len(rows) + idx,
                    'category_name': category_name,
                    'category_url': category_url,
                    'market_cap': market_cap_text,
                    'change_24h': change_24h_text,
                    'volume_24h': volume_text,
                    'page': page_num,
                    'scraped_at': datetime.now().isoformat()
                }

                categories_data.append(category_data)
                print(f"  ✓ {idx}. {category_name}")

            except Exception as e:
                print(f"  ✗ Error parsing row {idx}: {str(e)}")
                continue

        return categories_data

    except TimeoutException:
        print(f"  ⏱️ Timeout waiting for page {page_num} to load")
        return []
    except Exception as e:
        print(f"  ❌ Error scraping page {page_num}: {str(e)}")
        return []

def click_next_page(driver):
    """Try to click the next page button"""
    try:
        # Look for pagination buttons
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a[rel='next'], button[aria-label='Next'], .pagination .next:not(.disabled)")

        if not next_buttons:
            # Try alternative selectors
            next_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next')]")

        if next_buttons:
            next_button = next_buttons[0]

            # Check if button is disabled
            if 'disabled' in next_button.get_attribute('class'):
                print("  📍 Next button is disabled (last page)")
                return False

            # Scroll to button and click
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            next_button.click()
            time.sleep(3)  # Wait for new page to load

            return True
        else:
            print("  📍 No next button found")
            return False

    except Exception as e:
        print(f"  ❌ Error clicking next page: {str(e)}")
        return False

def scrape_category_coins(driver, category_url, category_name):
    """Visit a category page and scrape the coins in it"""
    print(f"\n🔍 Scraping coins from category: {category_name}")

    try:
        driver.get(category_url)

        # Wait for coin table to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )

        time.sleep(2)

        # Find all coin rows
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")[:50]  # Top 50 coins per category

        coins = []

        for row in rows:
            try:
                # Extract coin name and symbol
                name_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) a")
                coin_name = name_elem.text.strip()
                coin_url = name_elem.get_attribute("href")
                coin_id = coin_url.split('/')[-1] if coin_url else ""

                # Extract symbol
                try:
                    symbol_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) .tw-text-gray-500")
                    symbol = symbol_elem.text.strip()
                except:
                    symbol = ""

                # Extract price
                try:
                    price_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)")
                    price_text = price_elem.text.strip()
                except:
                    price_text = "N/A"

                # Extract market cap
                try:
                    mcap_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(7)")
                    mcap_text = mcap_elem.text.strip()
                except:
                    mcap_text = "N/A"

                coin_data = {
                    'coin_id': coin_id,
                    'coin_name': coin_name,
                    'symbol': symbol,
                    'price': price_text,
                    'market_cap': mcap_text,
                    'category': category_name,
                    'category_url': category_url,
                    'scraped_at': datetime.now().isoformat()
                }

                coins.append(coin_data)

            except Exception as e:
                continue

        print(f"  ✓ Extracted {len(coins)} coins from {category_name}")
        return coins

    except Exception as e:
        print(f"  ❌ Error scraping category coins: {str(e)}")
        return []

def main():
    """Main scraper function"""
    print("🌙 Moon Dev's CoinGecko Trending Categories Scraper 🚀")
    print(f"⚙️ Configuration:")
    print(f"  • Start URL: {START_URL}")
    print(f"  • Output File: {OUTPUT_FILE.absolute()}")
    print(f"  • Max Pages: {MAX_PAGES}")

    driver = None
    all_categories = []
    all_coins = []

    try:
        driver = setup_driver()

        # Load first page
        print(f"\n🌐 Loading {START_URL}...")
        driver.get(START_URL)

        page_num = 1

        while page_num <= MAX_PAGES:
            # Scrape current page
            categories = scrape_page(driver, page_num)

            if not categories:
                print(f"  ⚠️ No data found on page {page_num}, stopping")
                break

            all_categories.extend(categories)

            # Optionally scrape coins from each category (can be slow)
            # Uncomment the section below if you want to scrape coins too
            """
            for cat in categories[:5]:  # Scrape top 5 categories per page
                category_coins = scrape_category_coins(driver, cat['category_url'], cat['category_name'])
                all_coins.extend(category_coins)
                time.sleep(2)  # Rate limiting
            """

            # Try to go to next page
            if not click_next_page(driver):
                print("\n📍 Reached last page or pagination failed")
                break

            page_num += 1
            time.sleep(2)  # Rate limiting between pages

        # Save categories to CSV
        if all_categories:
            df_categories = pd.DataFrame(all_categories)

            # Create output directory
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Save to CSV
            df_categories.to_csv(OUTPUT_FILE, index=False)

            print(f"\n✨ Scraping Complete!")
            print(f"📊 Total categories scraped: {len(all_categories)}")
            print(f"💾 Saved to: {OUTPUT_FILE.absolute()}")

            # Show top 10
            print(f"\n🔥 Top 10 Trending Categories:")
            for _, row in df_categories.head(10).iterrows():
                print(f"  {row['rank']:2d}. {row['category_name']}")

        # Save coins if any were scraped
        if all_coins:
            coins_file = OUTPUT_FILE.parent / "trending_categories_coins_detailed.csv"
            df_coins = pd.DataFrame(all_coins)
            df_coins.to_csv(coins_file, index=False)
            print(f"💾 Coins saved to: {coins_file.absolute()}")
            print(f"📊 Total coins scraped: {len(all_coins)}")

    except KeyboardInterrupt:
        print("\n👋 Scraping cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        if driver:
            print("\n🔒 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    main()

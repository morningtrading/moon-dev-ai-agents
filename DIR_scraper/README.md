# CoinGecko Trending Coins Scraper

**Author:** Moon Dev
**Purpose:** Scrape trending coins from CoinGecko categories with full market data

---

## 📁 Files

1. **`scrape_trending_coins.py`** - Main scraper (Selenium + Firefox)
   - Scrapes trending categories from CoinGecko
   - Extracts individual coins from each category
   - Outputs: `trending_coins_data.csv`

2. **`enrich_coin_data.py`** - Data enricher (CoinGecko API)
   - Takes coin IDs from scraper
   - Fetches complete market data via API
   - Outputs: `trending_coins_enriched.csv`

3. **`trending_coins_data.csv`** - Raw scraped data (130 coins)

4. **`trending_coins_enriched.csv`** - **FINAL OUTPUT** with complete data

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install selenium webdriver-manager pandas requests python-dotenv
```

### Usage

**Step 1:** Scrape trending coins (takes 2-3 minutes)
```bash
python DIR_scraper/scrape_trending_coins.py
```

**Step 2:** Enrich with market data
```bash
python DIR_scraper/enrich_coin_data.py
```

---

## 📊 Output Data

### `trending_coins_enriched.csv` contains:

| Column | Description |
|--------|-------------|
| `coin_id` | CoinGecko coin ID |
| `coin_name` | Full coin name |
| `symbol` | Trading symbol |
| `price` | Current USD price |
| `price_change_1h_pct` | **1 hour price change %** |
| `price_change_24h_pct` | **24 hour price change %** |
| `price_change_7d_pct` | **7 day price change %** |
| `market_cap` | Total market capitalization |
| `volume_24h` | 24 hour trading volume |
| `market_cap_rank` | Rank by market cap |
| `high_24h` | 24h high price |
| `low_24h` | 24h low price |
| `circulating_supply` | Circulating supply |
| `total_supply` | Total supply |
| `ath` | All-time high price |
| `ath_date` | Date of ATH |
| `atl` | All-time low price |
| `atl_date` | Date of ATL |
| `category` | Trending category |
| `scraped_at` | Timestamp |

---

## 📈 Sample Data

```
Coin Name             Symbol  Price     1h%    24h%     7d%      Volume 24h    Market Cap
Dogecoin DOGE         DOGE    $0.158    1.1%   -4.6%   -19.6%    $4.05B       $24.02B
Shiba Inu SHIB        SHIB    $0.000009 0.3%   -5.1%   -14.2%    $271.45M     $5.14B
MemeCore M            M       $2.38     1.8%    0.5%    4.2%     $15.19M      $4.03B
Pepe PEPE             PEPE    $0.000005 0.8%   -4.3%   -21.3%    $687.64M     $2.30B
Official Trump TRUMP  TRUMP   $7.24    -1.4%    0.3%    5.1%     $950.14M     $1.45B
```

---

## ⚙️ Configuration

### Scraper Settings (`scrape_trending_coins.py`)
```python
MAX_CATEGORIES = 20          # Maximum categories to scrape
MAX_COINS_PER_CATEGORY = 50  # Max coins per category
```

### Enricher Settings (`enrich_coin_data.py`)
```python
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")  # Optional
```

---

## 🔥 Categories Scraped

- CeFi
- Binance HODLer Airdrops
- Meme
- Prediction Markets
- Decentralized Exchange (DEX)
- And more...

---

## 📝 Notes

- **No API key needed** for basic usage (uses public endpoints)
- **Rate limiting** built-in (1.5s between batches)
- **Headless mode** - Firefox runs in background
- **Duplicate removal** - Coins appearing in multiple categories are deduplicated
- **Missing data** - Some coins may have N/A values if not available from CoinGecko

---

## 🛠️ Troubleshooting

**Issue:** "Cannot find Chrome binary"
**Solution:** Script uses Firefox by default. Make sure Firefox is installed.

**Issue:** "No categories found"
**Solution:** CoinGecko may have changed their HTML structure. Check debug screenshots.

**Issue:** "No market data retrieved"
**Solution:** Check your internet connection and CoinGecko API status.

---

## 📊 Stats from Last Run

- **Total coins scraped:** 130
- **Unique coins:** 130
- **Coins with complete data:** 117
- **Categories scraped:** 4
- **Execution time:** ~3 minutes

---

**Built with 🌙 by Moon Dev**

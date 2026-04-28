
import random
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

# Hardcoded currency conversion rates to LKR for demo purposes
CURRENCY_RATES = {
    "GBP": 400.0,   # British Pound
    "EUR": 350.0,   # Euro
    "USD": 300.0,   # US Dollar
    "LKR": 1.0,     # Sri Lankan Rupee
    # Add more as needed
}

def get_currency_and_convert(price: float, country: str) -> tuple[float, str, float]:
    """
    Returns (converted_price, currency, original_price)
    """
    # Map country to currency (customize as needed)
    country_currency = {
        "United Kingdom": "GBP",
        "Germany": "EUR",
        "France": "EUR",
        "Finland": "EUR",
        "USA": "USD",
        "United States": "USD",
        "Sri Lanka": "LKR",
        # Add more as needed
    }
    currency = country_currency.get(country, "LKR")
    rate = CURRENCY_RATES.get(currency, 1.0)
    price_lkr = round(price * rate, 2)
    return price_lkr, currency, price

def load_product_prices_from_csv(
    csv_path: str = "data/data.csv",
    products: Optional[List[str]] = None,
    countries: Optional[List[str]] = None,
    sample_size: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Load product price data from a CSV file and filter/sample as needed.

    Args:
        csv_path: Path to the CSV file.
        products: List of product names to filter (matches in Description).
        countries: List of countries/stores to filter (matches in Country).
        sample_size: Number of random samples to return (after filtering).

    Returns:
        List of dicts with keys: store, title, price, currency
    """
    results = []
    file_path = Path(csv_path)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    try:
        f = file_path.open("r", encoding="utf-8")
        reader = csv.DictReader(f)
        for row in reader:
            desc = row.get("Description", "").strip()
            price = row.get("UnitPrice", "").strip()
            country = row.get("Country", "").strip()
            if not desc or not price or not country:
                continue
            try:
                price_val = float(price)
            except ValueError:
                continue
            if price_val <= 0:
                continue
            if products and not any(p.lower() in desc.lower() for p in products):
                continue
            if countries and country not in countries:
                continue
            price_lkr, currency, orig_price = get_currency_and_convert(price_val, country)
            results.append(
                {
                    "store": country,
                    "title": desc,
                    "price": price_lkr,
                    "currency": "LKR",
                    "price_lkr": price_lkr,
                    "price_original": round(orig_price, 2),
                    "currency_original": currency,
                }
            )
        f.close()
    except UnicodeDecodeError:
        # Fallback for non-UTF-8 CSVs (e.g., latin1/Windows-1252)
        with file_path.open("r", encoding="latin1") as f:
            reader = csv.DictReader(f)
            for row in reader:
                desc = row.get("Description", "").strip()
                price = row.get("UnitPrice", "").strip()
                country = row.get("Country", "").strip()
                if not desc or not price or not country:
                    continue
                try:
                    price_val = float(price)
                except ValueError:
                    continue
                if price_val <= 0:
                    continue
                if products and not any(p.lower() in desc.lower() for p in products):
                    continue
                if countries and country not in countries:
                    continue
                price_lkr, currency, orig_price = get_currency_and_convert(price_val, country)
                results.append(
                    {
                        "store": country,
                        "title": desc,
                        "price": price_lkr,
                        "currency": "LKR",
                        "price_lkr": price_lkr,
                        "price_original": round(orig_price, 2),
                        "currency_original": currency,
                    }
                )
    if sample_size and len(results) > sample_size:
        results = random.sample(results, sample_size)
    return results

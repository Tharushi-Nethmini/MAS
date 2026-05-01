import csv
from typing import List, Dict

def load_market_data(product_query: str, csv_path: str = "data/data.csv") -> List[Dict]:
    """
    Load market data for a given product from a CSV file.
    Returns a list of offers (store, price, available, description).
    """
    offers = []
    try:
        with open(csv_path, newline='', encoding='utf-8-sig', errors='replace') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    price = float(row["UnitPrice"])
                except Exception:
                    continue
                if product_query.lower() in row["Description"].lower() and price > 0:
                    offers.append({
                        "store": row["Country"],
                        "price": price,
                        "available": int(row["Quantity"]) > 0,
                        "description": row["Description"]
                    })
    except Exception as e:
        print(f"Error loading market data: {e}")
    return offers

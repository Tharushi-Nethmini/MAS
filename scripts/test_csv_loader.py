from src.mas.tools.csv_loader import load_product_prices_from_csv

# You can customize these parameters as needed
products = None  # e.g., ["apple", "milk"]
countries = None  # e.g., ["United Kingdom", "Sri Lanka"]
sample_size = 10  # Number of random samples to display

data = load_product_prices_from_csv(
    csv_path="data/data.csv",
    products=products,
    countries=countries,
    sample_size=sample_size
)

for item in data:
    print(item)

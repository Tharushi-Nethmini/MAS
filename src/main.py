from state import MASState
from agents import ProductSearchAgent, MarketAggregatorAgent, ComparisonAgent, OrderAgent, DeliveryAgent

def main():
    state = MASState()
    # Prompt the user for the product name
    product_query = input("Enter product name to search: ").strip()
    state.product_query = product_query if product_query else "Milk"

    ProductSearchAgent().run(state)
    MarketAggregatorAgent().run(state)

    # --- Data Validation Step (same as Member 5) ---
    # Only use offers scraped for the current product query (matching step-by-step agents)
    current_product = state.product_query
    offers_for_product = state.market_data.get(current_product, [])

    # Use the same normalization/validation as Member 5
    from mas.agents.data_validator import _normalize_item
    validated = []
    seen = set()
    for item in offers_for_product:
        normalized = _normalize_item(item)
        if not normalized:
            continue
        dedupe_key = (normalized["store"], normalized["price"], normalized["currency"])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        validated.append(normalized)

    # Improved: Token-based matching for product query in title or store
    def matches_query(item, query):
        query_tokens = set(query.lower().split())
        title = item.get("title", "").lower()
        store = item.get("store", "").lower()
        return any(token in title or token in store for token in query_tokens)

    filtered_validated = [item for item in validated if matches_query(item, state.product_query)]
    # If no offers match, fall back to all validated offers to avoid empty output
    if not filtered_validated:
        filtered_validated = validated

    state.validated_items = filtered_validated
    if state.products:
        state.market_data[state.products[0]] = filtered_validated

    ComparisonAgent().run(state)
    OrderAgent().run(state)
    DeliveryAgent().run(state)

    print("\n--- Validated Market Data Summary ---")
    offers = filtered_validated
    offers_sorted = sorted(offers, key=lambda x: x.get('price', float('inf')))
    top_offers = offers_sorted[:5]
    print(f"Total validated offers: {len(offers)}")
    stores = set(item.get('store') for item in offers)
    print(f"Stores found: {', '.join(sorted(stores))}")
    if offers:
        prices = [item['price'] for item in offers if isinstance(item.get('price'), (int, float))]
        if prices:
            print(f"Min price: {min(prices):.2f}, Max price: {max(prices):.2f}, Average price: {sum(prices)/len(prices):.2f}")
    print("\nTop 5 Cheapest Validated Offers:")
    for item in top_offers:
        print(f"- {item['title']} | Store: {item['store']} | Price: {item['price']} {item['currency']}")

    print("\n--- Comparison ---")
    print(state.comparison)

    print("\n--- Selected Store ---")
    print(state.selected_store)

    print("\n--- Order Details ---")
    print(state.order_details)

    print("\n--- Delivery Status ---")
    print(state.delivery_status)

if __name__ == "__main__":
    main()

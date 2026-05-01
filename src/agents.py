from state import MASState
from typing import Dict, List

class ProductSearchAgent:
    """
    Agent to search for products based on user query.
    """
    def run(self, state: MASState) -> None:
        # Use the user's product query as the only product
        if state.product_query and state.product_query.strip():
            state.products = [state.product_query.strip()]
        else:
            state.products = ["Milk"]

class MarketAggregatorAgent:
    """
    Agent to find supermarkets/stores and collect price/availability data for products.
    """
    def run(self, state: MASState) -> None:
        # Use real data from data/data.csv
        from data_utils import load_market_data
        state.market_data = {}
        for product in state.products:
            offers = load_market_data(product)
            # Fallback to dummy data if no offers found
            if not offers:
                offers = [
                    {"store": "SuperMart", "price": 250.0, "available": True, "description": product},
                    {"store": "QuickShop", "price": 275.0, "available": True, "description": product},
                    {"store": "BudgetMart", "price": 240.0, "available": False, "description": product}
                ]
            state.market_data[product] = offers

class ComparisonAgent:
    """
    Agent to compare prices and return best store, best price, min, max, and average price.
    """
    def run(self, state: MASState) -> None:
        # Example: compare for first product in list
        if not state.products:
            return
        product = state.products[0]
        offers = state.market_data.get(product, [])
        if offers:
            prices = [o["price"] for o in offers]
            best_offer = min(offers, key=lambda x: x["price"])
            state.comparison = {
                "best_store": best_offer["store"],
                "best_price": best_offer["price"],
                "min_price": min(prices),
                "max_price": max(prices),
                "average_price": sum(prices) / len(prices)
            }

class OrderAgent:
    """
    Agent to place an order for the selected product at the chosen store.
    """
    def run(self, state: MASState) -> None:
        state.selected_store = state.comparison.get("best_store")
        state.order_details = {
            "product": state.products[0] if state.products else None,
            "store": state.selected_store,
            "price": state.comparison.get("best_price")
        }

class DeliveryAgent:
    """
    Agent to arrange delivery and update delivery status.
    """
    def run(self, state: MASState) -> None:
        state.delivery_status = "Delivered"

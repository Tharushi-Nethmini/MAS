from typing import List, Dict, Optional

class MASState:
    """
    Shared state object for the Multi-Agent System workflow.
    Holds product queries, search results, market data, comparison results, order, and delivery status.
    """
    def __init__(self):
        self.product_query: Optional[str] = None
        self.products: List[str] = []
        self.market_data: Dict[str, List[Dict]] = {}
        self.comparison: Dict[str, any] = {}
        self.selected_store: Optional[str] = None
        self.order_details: Dict[str, any] = {}
        self.delivery_status: Optional[str] = None

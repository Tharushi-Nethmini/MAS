from __future__ import annotations

from typing import Any


def is_valid_price(price: Any) -> bool:
    """Check if a price value is valid and positive.
    
    Args:
        price: The price value to validate.
        
    Returns:
        True if price is a valid positive number, False otherwise.
    """
    try:
        numeric_price = float(price)
        return numeric_price > 0
    except (TypeError, ValueError):
        return False


def normalize_store_name(store: Any) -> str:
    """Normalize a store name for consistency.
    
    Args:
        store: Raw store name from scraped data.
        
    Returns:
        Normalized store name as a string, or empty string if invalid.
    """
    if not store:
        return ""
    return str(store).strip()


def normalize_product_title(title: Any) -> str:
    """Normalize a product title for consistency.
    
    Args:
        title: Raw product title from scraped data.
        
    Returns:
        Normalized product title or 'Unknown product' if empty.
    """
    if not title:
        return "Unknown product"
    normalized = str(title).strip()
    return normalized if normalized else "Unknown product"


def normalize_currency(currency: Any) -> str:
    """Normalize currency code.
    
    Args:
        currency: Raw currency value from scraped data.
        
    Returns:
        Normalized currency code, defaults to 'LKR'.
    """
    if not currency:
        return "LKR"
    normalized = str(currency).strip().upper()
    return normalized if normalized else "LKR"


def round_price(price: float, decimal_places: int = 2) -> float:
    """Round a price to the specified number of decimal places.
    
    Args:
        price: Price value to round.
        decimal_places: Number of decimal places to round to.
        
    Returns:
        Rounded price value.
    """
    try:
        return round(float(price), decimal_places)
    except (TypeError, ValueError):
        return 0.0


def extract_valid_offer(item: dict[str, Any]) -> dict[str, Any] | None:
    """Extract and validate a single offer item.
    
    Args:
        item: Raw offer dictionary from scraped data.
        
    Returns:
        Validated offer dictionary or None if invalid.
    """
    try:
        store = normalize_store_name(item.get("store", ""))
        title = normalize_product_title(item.get("title", ""))
        price = float(item.get("price", 0))
        currency = normalize_currency(item.get("currency", "LKR"))
        
        if not store or price <= 0:
            return None
        
        return {
            "store": store,
            "title": title,
            "price": round_price(price),
            "currency": currency,
        }
    except (TypeError, ValueError):
        return None


def detect_duplicate_offers(
    offers: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Detect and remove duplicate offers from a list.
    
    Args:
        offers: List of offer dictionaries.
        
    Returns:
        Tuple of (unique offers list, duplicate count).
    """
    seen: set[tuple[str, str, float]] = set()
    unique_offers = []
    duplicate_count = 0

    for offer in offers:
        # Extract offer keys for deduplication
        store = offer.get("store", "")
        title = offer.get("title", "")
        try:
            price = float(offer.get("price", 0))
        except (TypeError, ValueError):
            price = 0.0

        key = (store, title, price)
        if key in seen:
            duplicate_count += 1
        else:
            seen.add(key)
            unique_offers.append(offer)

    return unique_offers, duplicate_count


def categorize_price(
    price: float,
    average_price: float,
    lower_threshold: float = 0.92,
    upper_threshold: float = 1.08,
) -> str:
    """Categorize a price as Budget, Standard, or Premium.
    
    Args:
        price: Price to categorize.
        average_price: Average price for reference.
        lower_threshold: Lower bound multiplier for Budget category.
        upper_threshold: Upper bound multiplier for Premium category.
        
    Returns:
        Category name: 'Budget', 'Standard', or 'Premium'.
    """
    if average_price <= 0:
        return "Standard"

    lower_bound = average_price * lower_threshold
    upper_bound = average_price * upper_threshold

    if price <= lower_bound:
        return "Budget"
    elif price >= upper_bound:
        return "Premium"
    else:
        return "Standard"


def assign_categories_to_offers(
    offers: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Assign price categories (Budget/Standard/Premium) to offers.
    
    Args:
        offers: List of validated offer dictionaries.
        
    Returns:
        Tuple of (offers with category field, category summary dict).
    """
    if not offers:
        return [], {"Budget": 0, "Standard": 0, "Premium": 0}

    average_price = sum(offer["price"] for offer in offers) / len(offers)
    category_summary = {"Budget": 0, "Standard": 0, "Premium": 0}

    categorized_offers = []
    for offer in offers:
        category = categorize_price(offer["price"], average_price)
        offer_with_category = {**offer, "category": category}
        categorized_offers.append(offer_with_category)
        category_summary[category] += 1

    return categorized_offers, category_summary


def compute_quality_score(
    valid_count: int,
    total_count: int,
) -> float:
    """Compute a quality score for the validation process.
    
    Args:
        valid_count: Number of valid/accepted offers.
        total_count: Total number of offers processed.
        
    Returns:
        Quality score as a percentage (0.0 to 100.0).
    """
    if total_count == 0:
        return 0.0
    return round(100.0 * valid_count / total_count, 2)


def generate_validation_summary(
    valid_count: int,
    anomaly_count: int,
    quality_score: float,
    category_summary: dict[str, int],
) -> str:
    """Generate a human-readable validation summary.
    
    Args:
        valid_count: Number of valid offers.
        anomaly_count: Number of anomalies/errors detected.
        quality_score: Computed quality score.
        category_summary: Dictionary with category counts.
        
    Returns:
        Formatted validation summary string.
    """
    if valid_count == 0:
        return (
            f"No valid offers were found after validation. "
            f"Anomaly count: {anomaly_count}."
        )

    category_details = ", ".join(
        f"{cat}: {count}" for cat, count in category_summary.items()
    )

    return (
        f"Validated {valid_count} offers ({category_details}) "
        f"with {anomaly_count} anomalies removed. "
        f"Quality score: {quality_score}%."
    )


def get_price_statistics(offers: list[dict[str, Any]]) -> dict[str, float]:
    """Compute price statistics from offers.
    
    Args:
        offers: List of offer dictionaries with 'price' field.
        
    Returns:
        Dictionary with min, max, average, and median prices.
    """
    if not offers:
        return {
            "min_price": 0.0,
            "max_price": 0.0,
            "average_price": 0.0,
            "median_price": 0.0,
        }

    prices = [offer["price"] for offer in offers]
    sorted_prices = sorted(prices)

    min_price = min(prices)
    max_price = max(prices)
    average_price = sum(prices) / len(prices)

    # Compute median
    n = len(sorted_prices)
    if n % 2 == 0:
        median_price = (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2
    else:
        median_price = sorted_prices[n // 2]

    return {
        "min_price": round_price(min_price),
        "max_price": round_price(max_price),
        "average_price": round_price(average_price),
        "median_price": round_price(median_price),
    }


def flag_price_outliers(
    offers: list[dict[str, Any]],
    std_dev_threshold: float = 2.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Identify price outliers using statistical methods.
    
    Args:
        offers: List of offer dictionaries with 'price' field.
        std_dev_threshold: Number of standard deviations for outlier detection.
        
    Returns:
        Tuple of (normal offers, outlier offers).
    """
    if not offers or len(offers) < 2:
        return offers, []

    prices = [offer["price"] for offer in offers]
    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    std_dev = variance ** 0.5

    if std_dev == 0:
        return offers, []

    normal = []
    outliers = []

    for offer in offers:
        z_score = abs((offer["price"] - mean) / std_dev)
        if z_score > std_dev_threshold:
            outliers.append(offer)
        else:
            normal.append(offer)

    return normal, outliers


def validate_offers_batch(
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate a batch of scraped offers with comprehensive checks.
    
    This function performs:
    1. Individual offer validation (price, store, title)
    2. Duplicate detection and removal
    3. Price categorization (Budget/Standard/Premium)
    4. Quality scoring
    5. Summary generation
    
    Args:
        items: List of raw scraped offer dictionaries.
        
    Returns:
        Dictionary with validated_items, quality_score, category_summary, and notes.
    """
    if not items:
        return {
            "validated_items": [],
            "quality_score": 0.0,
            "category_summary": {"Budget": 0, "Standard": 0, "Premium": 0},
            "validation_notes": "No offers provided for validation.",
        }

    # Step 1: Extract valid offers
    valid_offers = []
    invalid_count = 0
    for item in items:
        extracted = extract_valid_offer(item)
        if extracted:
            valid_offers.append(extracted)
        else:
            invalid_count += 1

    # Step 2: Detect duplicates
    unique_offers, duplicate_count = detect_duplicate_offers(valid_offers)

    # Step 3: Categorize prices
    categorized_offers, category_summary = assign_categories_to_offers(unique_offers)

    # Step 4: Compute quality score
    total_processed = len(items)
    quality_score = compute_quality_score(len(categorized_offers), total_processed)

    # Step 5: Generate summary
    anomaly_count = invalid_count + duplicate_count
    validation_notes = generate_validation_summary(
        len(categorized_offers),
        anomaly_count,
        quality_score,
        category_summary,
    )

    return {
        "validated_items": categorized_offers,
        "quality_score": quality_score,
        "category_summary": category_summary,
        "validation_notes": validation_notes,
    }

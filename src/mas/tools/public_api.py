from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

# Import the CSV loader
from src.mas.tools.csv_loader import load_product_prices_from_csv
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.mas.config import settings
from src.mas.llm import ask_ollama


def _deterministic_fallback_profiles(product_name: str) -> list[tuple[str, float, str]]:
    """Return generic deterministic fallback profiles when model output is unavailable."""

    key = product_name.strip().lower()
    seed = sum(ord(ch) for ch in key)
    base = 100.0 + float(seed % 2000)

    return [
        ("Keells", round(base, 2), "Standard"),
        ("Glomark", round(base * 1.06, 2), "Premium"),
        ("Arpico", round(base * 0.94, 2), "Budget"),
    ]


def _parse_llm_profiles(raw_text: str) -> list[tuple[str, float, str]]:
    """Parse Ollama JSON output into normalized store profiles."""

    candidate = raw_text.strip()
    if not candidate.startswith("["):
        match = re.search(r"\[.*\]", candidate, flags=re.DOTALL)
        if not match:
            raise ValueError("No JSON array found in model output.")
        candidate = match.group(0)

    data = json.loads(candidate)
    if not isinstance(data, list):
        raise ValueError("Model output must be a JSON array.")

    profiles: list[tuple[str, float, str]] = []
    for entry in data[:3]:
        if not isinstance(entry, dict):
            continue
        store = str(entry.get("store") or entry.get("source") or entry.get("market") or "").strip()
        label = str(entry.get("label") or entry.get("condition") or entry.get("tier") or "Offer").strip() or "Offer"
        try:
            price = float(entry.get("price_lkr") or entry.get("price") or entry.get("amount") or 0)
        except (TypeError, ValueError):
            continue
        if not store or price <= 0:
            continue
        profiles.append((store, round(price, 2), label))

    if len(profiles) < 3:
        raise ValueError("Model output did not include enough valid profiles.")
    return profiles


def _llm_offline_profiles(product_name: str, model: str | None = None) -> list[tuple[str, float, str]]:
    """Generate store and price profiles for any product using local Ollama."""

    system_prompt = (
        "You generate realistic Sri Lankan product price samples. "
        "Return ONLY a JSON array of exactly 3 objects with keys: "
        "store, label, price_lkr. No markdown, no explanations."
    )
    user_prompt = (
        f"Product: {product_name}\n"
        "Choose realistic marketplaces/stores for this product type and plausible LKR prices. "
        "Example format: "
        '[{"store":"X","label":"New","price_lkr":12345.0}, ...]'
    )

    primary_model = model or settings.default_model
    candidate_models = [primary_model]
    if primary_model != "mistral:latest":
        candidate_models.append("mistral:latest")

    last_error: Exception | None = None
    for candidate in candidate_models:
        try:
            response = ask_ollama(
                base_url=settings.ollama_base_url,
                model=candidate,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                timeout_seconds=120,
            )
            return _parse_llm_profiles(response)
        except Exception as exc:
            last_error = exc
            continue

    if last_error is not None:
        raise last_error
    raise RuntimeError("Unable to generate LLM offline profiles.")


def _offline_html_catalog(product_name: str, model: str | None = None) -> list[tuple[str, str]]:
    """Return offline HTML snippets generated from Ollama-driven sample profiles."""

    p = product_name.strip() or "coconut"
    use_llm = os.getenv("MAS_OFFLINE_USE_LLM", "0") == "1"
    if use_llm:
        try:
            profiles = _llm_offline_profiles(p, model=model)
        except Exception:
            profiles = _deterministic_fallback_profiles(p)
    else:
        profiles = _deterministic_fallback_profiles(p)

    catalog: list[tuple[str, str]] = []
    for store, price, label in profiles:
        html = (
            "<html><body><div class='product-card'>"
            f"<h2>{p} {label}</h2><span class='price'>LKR {price:.2f}</span>"
            "</div></body></html>"
        )
        catalog.append((store, html))
    return catalog


def _shopify_endpoint_from_url(url: str) -> tuple[str, str]:
    """Return store name and Shopify products.json endpoint for a given source URL."""

    parsed = urlparse(url)
    host = parsed.netloc.strip()
    if not host:
        return "", ""

    scheme = parsed.scheme or "https"
    base = f"{scheme}://{host}"
    path = parsed.path or ""

    if "products.json" in path:
        endpoint = f"{base}{path}"
        if parsed.query:
            endpoint = f"{endpoint}?{parsed.query}"
        elif "limit=" not in endpoint:
            endpoint = f"{endpoint}?limit=250"
    else:
        endpoint = f"{base}/products.json?limit=250"

    store_name = host.replace("www.", "")
    return store_name, endpoint


def _snapshot_paths(endpoint: str) -> tuple[str, str]:
    """Return snapshot mode and filepath for a Shopify endpoint."""

    mode = os.getenv("MAS_SHOPIFY_SNAPSHOT_MODE", "off").strip().lower()
    root = os.getenv("MAS_SHOPIFY_SNAPSHOT_DIR", "reports/snapshots")
    digest = hashlib.sha1(endpoint.encode("utf-8")).hexdigest()[:16]
    path = os.path.join(root, f"shopify_{digest}.json")
    return mode, path


def _load_shopify_payload(endpoint: str) -> dict[str, Any]:
    """Load Shopify payload from live endpoint or snapshot record/replay mode."""

    mode, snapshot_path = _snapshot_paths(endpoint)

    if mode == "replay" and os.path.exists(snapshot_path):
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}

    response = requests.get(endpoint, timeout=20)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        data = {}

    if mode == "record":
        os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def _extract_shopify_items(store_name: str, payload: dict[str, Any], product_name: str) -> list[dict[str, Any]]:
    """Extract deterministic item list from Shopify products payload."""

    products = payload.get("products", [])
    if not isinstance(products, list):
        return []

    query_tokens = [t for t in re.findall(r"[a-z0-9]+", product_name.lower()) if t]

    items: list[dict[str, Any]] = []
    for product in products:
        if not isinstance(product, dict):
            continue
        title = str(product.get("title", "")).strip()
        if not title:
            continue

        title_l = title.lower()
        if query_tokens and not all(token in title_l for token in query_tokens):
            continue

        variants = product.get("variants", [])
        if not isinstance(variants, list):
            continue

        for variant in variants:
            if not isinstance(variant, dict):
                continue
            raw_price = variant.get("price", "")
            try:
                price = float(raw_price)
            except (TypeError, ValueError):
                continue
            if price <= 0:
                continue

            variant_title = str(variant.get("title", "")).strip()
            full_title = title if variant_title.lower() in {"", "default title"} else f"{title} - {variant_title}"

            items.append(
                {
                    "store": store_name,
                    "title": full_title,
                    "price": round(price, 2),
                    "currency": "LKR",
                }
            )

    deduped = {(x["store"], x["title"], x["price"]): x for x in items}
    ordered = sorted(deduped.values(), key=lambda x: (float(x["price"]), x["store"], x["title"]))
    return ordered


def extract_prices_from_html(store_name: str, html: str, product_name: str) -> list[dict[str, Any]]:
    """Extract product price candidates from HTML content.

    Args:
        store_name: Store label for extracted entries.
        html: Raw HTML string.
        product_name: Product query used for relevance filtering.

    Returns:
        List of normalized item dictionaries with store, title, and price.
    """

    soup = BeautifulSoup(html, "html.parser")
    page_text = " ".join(soup.stripped_strings)
    if product_name.lower() not in page_text.lower():
        return []

    prefix_pattern = re.compile(r"(?:LKR|Rs\.?)\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE)
    suffix_pattern = re.compile(r"(\d+(?:\.\d{1,2})?)\s*LKR", re.IGNORECASE)
    matches = prefix_pattern.findall(page_text) + suffix_pattern.findall(page_text)

    items: list[dict[str, Any]] = []
    for raw in matches:
        try:
            price = float(raw)
        except ValueError:
            continue
        if price <= 0:
            continue
        items.append(
            {
                "store": store_name,
                "title": product_name,
                "price": round(price, 2),
                "currency": "LKR",
            }
        )
    return items


def scrape_prices(
    product_name: str,
    source_urls: list[str] | None = None,
    offline_mode: bool = False,
    model: str | None = None,
) -> list[dict[str, Any]]:
    """Scrape product prices from provided URLs or offline samples.

    Args:
        product_name: Product query term.
        source_urls: Optional list of target URLs.
        offline_mode: If true, uses local HTML snippets.

    Returns:
        List of item dictionaries with normalized fields.
    """

    collected: list[dict[str, Any]] = []

    # Always try online scraping first if URLs are provided
    if source_urls:
        for url in source_urls:
            try:
                store_name, endpoint = _shopify_endpoint_from_url(url)
                if endpoint:
                    payload = _load_shopify_payload(endpoint)
                    shopify_items = _extract_shopify_items(store_name, payload, product_name)
                    if shopify_items:
                        collected.extend(shopify_items)
                        continue

                response = requests.get(url, timeout=15)
                response.raise_for_status()
                html = response.text
                store_name = store_name or url.split("//")[-1].split("/")[0]
                collected.extend(extract_prices_from_html(store_name, html, product_name))
            except Exception:
                continue

    # If online scraping failed or returned nothing, and offline_mode is True, use dataset if available
    if (not collected) and offline_mode:
        # Try to load from dataset CSV.
        try:
            dataset_items = load_product_prices_from_csv(
                csv_path="data/data.csv",
                products=[product_name] if product_name else None,
                countries=None,
                sample_size=10,  # You can adjust or make this configurable
            )
            collected.extend(dataset_items)
        except Exception:
            pass

        # If dataset is empty or unavailable, fallback to deterministic offline HTML samples.
        if not collected:
            for store, html in _offline_html_catalog(product_name, model=model):
                collected.extend(extract_prices_from_html(store, html, product_name))

    return sorted(collected, key=lambda x: (float(x["price"]), x["store"], x["title"]))

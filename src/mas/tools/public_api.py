from __future__ import annotations

import re
from typing import Any

import requests
from bs4 import BeautifulSoup


def _offline_html_catalog(product_name: str) -> list[tuple[str, str]]:
    """Return offline HTML snippets that simulate e-commerce product cards."""

    p = product_name.strip() or "coconut"
    return [
        (
            "Glomark",
            (
                "<html><body><div class='product'>"
                f"<h2>{p} - 1kg</h2><span class='price'>LKR 120.00</span>"
                "</div></body></html>"
            ),
        ),
        (
            "Keells",
            (
                "<html><body><article class='item'>"
                f"<p class='name'>{p} premium</p><p class='amount'>Rs. 135.50</p>"
                "</article></body></html>"
            ),
        ),
        (
            "Arpico",
            (
                "<html><body><section class='listing'>"
                f"<span>{p} fresh</span><strong>110 LKR</strong>"
                "</section></body></html>"
            ),
        ),
    ]


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

    pattern = re.compile(r"(?:LKR|Rs\.?\s?|\b)(\d+(?:\.\d{1,2})?)", re.IGNORECASE)
    matches = pattern.findall(page_text)

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


def scrape_prices(product_name: str, source_urls: list[str] | None = None, offline_mode: bool = False) -> list[dict[str, Any]]:
    """Scrape product prices from provided URLs or offline samples.

    Args:
        product_name: Product query term.
        source_urls: Optional list of target URLs.
        offline_mode: If true, uses local HTML snippets.

    Returns:
        List of item dictionaries with normalized fields.
    """

    collected: list[dict[str, Any]] = []

    if offline_mode or not source_urls:
        for store, html in _offline_html_catalog(product_name):
            collected.extend(extract_prices_from_html(store, html, product_name))
        return collected

    for url in source_urls:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            html = response.text
            store_name = url.split("//")[-1].split("/")[0]
            collected.extend(extract_prices_from_html(store_name, html, product_name))
        except Exception:
            continue

    return collected

from __future__ import annotations

import os

from src.mas.web import create_app


def test_member_6_uses_submitted_single_scraped_price() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/member",
        json={
            "member": "6",
            "product_name": "coconut",
            "scraped_items": '{"store":"Glomark","price":120.0}',
            "use_scraped": True,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "120.00 LKR" in data["result"]["trend_summary"]


def test_member_6_rejects_invalid_scraped_json_instead_of_using_demo_prices() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/member",
        json={
            "member": "6",
            "product_name": "coconut",
            "scraped_items": '{"store":"Glomark","price":120.0',
            "use_scraped": True,
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Scraped items JSON is invalid" in data["error"]


def test_member_6_explicit_best_price_wins_over_demo_scraped_items() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/member",
        json={
            "member": "6",
            "product_name": "coconut",
            "best_price": "120.0",
            "scraped_items": "",
            "use_scraped": True,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "120.00 LKR" in data["result"]["trend_summary"]


def test_member_6_requires_real_scraped_or_best_price_instead_of_demo_prices() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/member",
        json={
            "member": "6",
            "product_name": "coconut",
            "scraped_items": "",
            "use_scraped": True,
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Run Member 2 first" in data["error"]


def test_member_3_reports_no_available_products_without_demo_prices(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/member",
        json={
            "member": "3",
            "product_name": "product-that-does-not-exist-xyz",
            "scraped_items": "",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    result = data["result"]
    assert result["scraped_items"] == []
    assert result["product_available"] is False
    assert result["best_store"] == "N/A"
    assert result["best_price"] == 0.0
    assert "No available products found" in result["analysis_summary"]


def test_member_5_reports_no_available_products_without_demo_prices(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/member",
        json={
            "member": "5",
            "product_name": "product-that-does-not-exist-xyz",
            "scraped_items": "",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    result = data["result"]
    assert result["scraped_items"] == []
    assert result["product_available"] is False
    assert result["validated_items"] == []
    assert "No available products found" in result["research_notes"]

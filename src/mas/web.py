from __future__ import annotations

import json
import os
import uuid

from flask import Flask, jsonify, render_template, request

from src.mas.agents.budgeter import budget_agent
from src.mas.agents.coordinator import coordinator_agent
from src.mas.agents.offer_validator import offer_validator_agent
from src.mas.agents.researcher import research_agent
from src.mas.agents.risk_reporter import risk_and_report_agent
from src.mas.agents.trend_analyzer import trend_analyzer_agent
from src.mas.config import settings
from src.mas.graph import build_graph


def _parse_json_items(value: str) -> list[dict[str, object]]:
    parsed = json.loads(value)
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    raise ValueError("Scraped items JSON must be an object or a list of objects.")


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.route("/", methods=["GET"])
    def index() -> str:
        return render_template(
            "index.html",
            default_model=settings.default_model,
            offline_mode=os.getenv("MAS_OFFLINE_MODE", "0") == "1",
        )

    @app.route("/api/compare", methods=["POST"])
    def compare() -> tuple[dict[str, object], int]:
        payload = request.get_json(silent=True) or {}
        product_name = str(payload.get("product_name", "")).strip()
        source_urls = str(payload.get("source_urls", ""))
        model = str(payload.get("model", settings.default_model)).strip() or settings.default_model

        if not product_name:
            return {"error": "Product name is required."}, 400

        sources = [item.strip() for item in source_urls.split(",") if item.strip()]
        trace_id = uuid.uuid4().hex[:10]
        state = {
            "trace_id": trace_id,
            "model": model,
            "user_request": product_name,
            "source_urls": sources,
            "meta": {"offline_mode": os.getenv("MAS_OFFLINE_MODE", "0") == "1"},
        }

        graph = build_graph()
        try:
            result = graph.invoke(state)
        except Exception as exc:
            return {
                "error": "MAS execution failed.",
                "details": str(exc),
                "trace_id": trace_id,
            }, 500

        return {
            "trace_id": trace_id,
            "result": result,
            "report_path": result.get("saved_report_path"),
            "report_pdf_path": result.get("saved_report_pdf_path"),
        }, 200

    @app.route("/api/member", methods=["POST"])
    def run_member() -> tuple[dict[str, object], int]:
        payload = request.get_json(silent=True) or {}
        member = str(payload.get("member", "")).strip()
        if member not in {"1", "2", "3", "4", "5", "6"}:
            return {"error": "Member must be a number between 1 and 6."}, 400

        trace_id = uuid.uuid4().hex[:10]
        product_name = str(payload.get("product_name", "")).strip()
        source_urls = [item.strip() for item in str(payload.get("source_urls", "")).split(",") if item.strip()]
        model = str(payload.get("model", settings.default_model)).strip() or settings.default_model
        best_price = payload.get("best_price")
        scraped_items = payload.get("scraped_items")
        scraped_items_provided = isinstance(scraped_items, str) and bool(scraped_items.strip())
        use_scraped = payload.get("use_scraped", member == "6")

        if isinstance(scraped_items, str):
            if scraped_items.strip():
                try:
                    scraped_items = _parse_json_items(scraped_items)
                except (TypeError, ValueError, json.JSONDecodeError) as exc:
                    return {"error": f"Scraped items JSON is invalid: {exc}", "trace_id": trace_id}, 400
            else:
                scraped_items = []
        elif not isinstance(scraped_items, list):
            scraped_items = []

        if member == "1":
            if not product_name:
                return {"error": "Request text is required for Member 1."}, 400
            state = {
                "trace_id": trace_id,
                "model": model,
                "user_request": product_name,
            }
            try:
                result = coordinator_agent(state)
            except Exception as exc:
                return {"error": "Coordinator failed.", "details": str(exc), "trace_id": trace_id}, 500

        elif member == "2":
            if not product_name:
                return {"error": "Product name is required for Member 2."}, 400
            state = {
                "trace_id": trace_id,
                "model": model,
                "product_name": product_name,
                "source_urls": source_urls,
            }
            try:
                result = research_agent(state)
            except Exception as exc:
                return {"error": "Web Scraper failed.", "details": str(exc), "trace_id": trace_id}, 500

        elif member == "3":
            if not product_name:
                return {"error": "Product name is required for Member 3."}, 400
            if not scraped_items:
                scraper_state = {
                    "trace_id": trace_id,
                    "model": model,
                    "product_name": product_name,
                    "source_urls": source_urls,
                }
                try:
                    scraper_result = research_agent(scraper_state)
                except Exception as exc:
                    return {"error": "Web Scraper failed before Price Analyzer.", "details": str(exc), "trace_id": trace_id}, 500
                scraped_items = scraper_result.get("scraped_items", [])
            else:
                scraper_result = {
                    "scraped_items": scraped_items,
                    "product_available": bool(scraped_items),
                    "research_notes": "Using submitted scraped items.",
                }
            state = {
                "trace_id": trace_id,
                "product_name": product_name,
                "scraped_items": scraped_items,
            }
            try:
                result = {**scraper_result, **budget_agent(state)}
            except Exception as exc:
                return {"error": "Price Analyzer failed.", "details": str(exc), "trace_id": trace_id}, 500

        elif member == "4":
            if not product_name:
                return {"error": "Request text is required for Member 4."}, 400
            state = {
                "trace_id": trace_id,
                "model": model,
                "user_request": product_name,
                "source_urls": source_urls,
                "meta": {"offline_mode": os.getenv("MAS_OFFLINE_MODE", "0") == "1"},
            }
            graph = build_graph()
            try:
                result = graph.invoke(state)
            except Exception as exc:
                return {"error": "Full pipeline failed.", "details": str(exc), "trace_id": trace_id}, 500

        elif member == "5":
            if not scraped_items:
                if not product_name:
                    return {"error": "Product name is required for Member 5 when scraped items are not provided."}, 400
                scraper_state = {
                    "trace_id": trace_id,
                    "model": model,
                    "product_name": product_name,
                    "source_urls": source_urls,
                }
                try:
                    scraper_result = research_agent(scraper_state)
                except Exception as exc:
                    return {"error": "Web Scraper failed before Offer Validator.", "details": str(exc), "trace_id": trace_id}, 500
                scraped_items = scraper_result.get("scraped_items", [])
            else:
                scraper_result = {
                    "scraped_items": scraped_items,
                    "product_available": bool(scraped_items),
                    "research_notes": "Using submitted scraped items.",
                }
            state = {
                "trace_id": trace_id,
                "scraped_items": scraped_items,
            }
            try:
                result = {**scraper_result, **offer_validator_agent(state)}
            except Exception as exc:
                return {"error": "Offer Validator failed.", "details": str(exc), "trace_id": trace_id}, 500

        else:
            if not product_name:
                return {"error": "Product name is required for Member 6."}, 400

            best_value = None
            if best_price not in (None, ""):
                try:
                    best_value = float(best_price)
                except (TypeError, ValueError):
                    return {"error": "Best price must be a valid number for Member 6.", "trace_id": trace_id}, 400
            elif use_scraped:
                if not scraped_items:
                    error = "Run Member 2 first, paste scraped items JSON, or enter Best price for Member 6."
                    if scraped_items_provided:
                        error = "Scraped items JSON must include at least one object with a valid price for Member 6."
                    return {"error": error, "trace_id": trace_id}, 400
                prices = []
                for item in scraped_items:
                    if isinstance(item, dict) and item.get("price") not in (None, ""):
                        try:
                            prices.append(float(item["price"]))
                        except (TypeError, ValueError):
                            continue
                if not prices:
                    return {"error": "Scraped items must contain valid price values for Member 6."}, 400
                best_value = min(prices)
            else:
                return {"error": "Best price is required when not using scraped items for Member 6."}, 400

            if best_value <= 0.0:
                return {"error": "Best price must be greater than 0 for Member 6."}, 400

            state = {
                "trace_id": trace_id,
                "product_name": product_name,
                "best_price": best_value,
            }
            try:
                result = trend_analyzer_agent(state)
            except Exception as exc:
                return {"error": "Trend Analyzer failed.", "details": str(exc), "trace_id": trace_id}, 500

        response = {
            "trace_id": trace_id,
            "result": result,
        }
        if member == "4":
            response["report_path"] = result.get("saved_report_path")
            response["report_pdf_path"] = result.get("saved_report_pdf_path")
        return response, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)

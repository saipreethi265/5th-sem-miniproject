from __future__ import annotations

import os
from functools import wraps
from typing import Any, Callable

from flask import Flask, jsonify, render_template, request

from assistant import human_rights_assistant
from awareness import AWARENESS_CONTENT
from complaint import create_complaint
from database import (
    create_case,
    create_database,
    delete_case,
    get_case,
    get_cases,
    get_dashboard_statistics,
    update_case,
)

app = Flask(__name__)

app.config.update(
    JSON_SORT_KEYS=False,
    MAX_CONTENT_LENGTH=64 * 1024,
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-in-production"),
)

VALID_STATUSES = {"Open", "In Review", "Referred", "Resolved", "Closed"}
VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}


def api_error(message: str, status_code: int = 400):
    return jsonify({"success": False, "message": message}), status_code


def require_json(view: Callable[..., Any]):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return api_error("The request must contain JSON.", 415)

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return api_error("Invalid JSON request.", 400)

        return view(data, *args, **kwargs)

    return wrapper


def clean_text(value: Any, maximum_length: int) -> str:
    if not isinstance(value, str):
        return ""

    return " ".join(value.strip().split())[:maximum_length]


@app.errorhandler(404)
def not_found(_error):
    return api_error("Resource not found.", 404)


@app.errorhandler(413)
def request_too_large(_error):
    return api_error("The request is too large.", 413)


@app.errorhandler(500)
def internal_error(_error):
    return api_error("An unexpected server error occurred.", 500)


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/assistant")
@require_json
def assistant_api(data: dict[str, Any]):
    question = clean_text(data.get("question"), 5000)

    if not question:
        return api_error("Please describe your concern.")

    result = human_rights_assistant(question)

    return jsonify(
        {
            "success": True,
            **result,
        }
    )


@app.post("/api/cases")
@require_json
def save_case_api(data: dict[str, Any]):
    name = clean_text(data.get("name"), 120)
    email = clean_text(data.get("email"), 180)
    phone = clean_text(data.get("phone"), 40)
    location = clean_text(data.get("location"), 200)
    description = clean_text(data.get("description"), 5000)
    consent = data.get("consent") is True

    if not name:
        return api_error("Please enter the complainant's name.")

    if len(name) < 2:
        return api_error("The name must contain at least two characters.")

    if not description:
        return api_error("Please describe the human-rights concern.")

    if len(description) < 15:
        return api_error("Please provide a more detailed description.")

    if not consent:
        return api_error("Consent is required before storing this case.")

    analysis = human_rights_assistant(description)

    case = create_case(
        name=name,
        email=email,
        phone=phone,
        location=location,
        description=description,
        category=analysis["category"],
        issue=analysis["issue"],
        priority=analysis["priority"],
    )

    return (
        jsonify(
            {
                "success": True,
                "message": "Case registered successfully.",
                "case": case,
            }
        ),
        201,
    )


@app.get("/api/cases")
def cases_api():
    search = clean_text(request.args.get("search", ""), 200)
    status = clean_text(request.args.get("status", ""), 30)
    category = clean_text(request.args.get("category", ""), 100)

    if status and status not in VALID_STATUSES:
        return api_error("Invalid case status.")

    records = get_cases(search=search, status=status, category=category)

    return jsonify(
        {
            "success": True,
            "count": len(records),
            "cases": records,
        }
    )


@app.get("/api/cases/<int:case_id>")
def case_details_api(case_id: int):
    case = get_case(case_id)

    if not case:
        return api_error("Case not found.", 404)

    return jsonify({"success": True, "case": case})


@app.patch("/api/cases/<int:case_id>")
@require_json
def update_case_api(data: dict[str, Any], case_id: int):
    status = clean_text(data.get("status"), 30)
    priority = clean_text(data.get("priority"), 30)
    notes = clean_text(data.get("notes"), 3000)

    if status and status not in VALID_STATUSES:
        return api_error("Invalid case status.")

    if priority and priority not in VALID_PRIORITIES:
        return api_error("Invalid case priority.")

    if not status and not priority and "notes" not in data:
        return api_error("No update fields were provided.")

    case = update_case(
        case_id=case_id,
        status=status or None,
        priority=priority or None,
        notes=notes if "notes" in data else None,
    )

    if not case:
        return api_error("Case not found.", 404)

    return jsonify(
        {
            "success": True,
            "message": "Case updated successfully.",
            "case": case,
        }
    )


@app.delete("/api/cases/<int:case_id>")
def delete_case_api(case_id: int):
    deleted = delete_case(case_id)

    if not deleted:
        return api_error("Case not found.", 404)

    return jsonify(
        {
            "success": True,
            "message": "Case deleted successfully.",
        }
    )


@app.post("/api/complaints")
@require_json
def complaint_api(data: dict[str, Any]):
    name = clean_text(data.get("name"), 120)
    description = clean_text(data.get("description"), 5000)
    location = clean_text(data.get("location"), 200)
    authority = clean_text(data.get("authority"), 200)

    if not name or not description:
        return api_error("Name and description are required.")

    if len(description) < 15:
        return api_error("Please provide a more detailed description.")

    analysis = human_rights_assistant(description)

    complaint_text = create_complaint(
        name=name,
        description=description,
        category=analysis["category"],
        location=location,
        authority=authority,
    )

    return jsonify(
        {
            "success": True,
            "category": analysis["category"],
            "priority": analysis["priority"],
            "complaint": complaint_text,
        }
    )


@app.get("/api/awareness")
def awareness_api():
    return jsonify(
        {
            "success": True,
            "content": AWARENESS_CONTENT,
        }
    )


@app.get("/api/statistics")
def statistics_api():
    return jsonify(
        {
            "success": True,
            "statistics": get_dashboard_statistics(),
        }
    )


@app.get("/api/export")
def export_cases_api():
    cases = get_cases()

    return jsonify(
        {
            "success": True,
            "exported_count": len(cases),
            "cases": cases,
        }
    )


if __name__ == "__main__":
    create_database()

    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )

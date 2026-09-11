from typing import Any, Dict, List

SUPPORTED_TYPES = {
    "invoice",
    "balance_sheet",
    "profit_and_loss",
    "cash_flow_statement",
}

def empty_extraction(document_type: str) -> Dict[str, Any]:
    base = {
        "document_type": document_type,
        "document_title": None,
        "entity_name": None,
        "statement_period": None,
        "currency": None,
        "header_fields": {},
        "line_items": [],
    }
    if document_type == "invoice":
        base.update({
            "invoice_number": None,
            "invoice_date": None,
            "vendor_name": None,
            "customer_name": None,
            "subtotal": None,
            "tax_amount": None,
            "discount": None,
            "total_amount": None,
            "line_items": [],
        })
    return base

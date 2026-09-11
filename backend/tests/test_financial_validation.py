from app.services.financial_validation_service import validate_invoice, validate_profit_and_loss

def test_invoice_pass():
    result = validate_invoice({
        "subtotal": {"value": 100},
        "tax_amount": {"value": 10},
        "discount": {"value": 0},
        "total_amount": {"value": 110},
        "line_items": []
    })
    assert result["overall_status"] == "PASS"

def test_invoice_fail():
    result = validate_invoice({
        "subtotal": {"value": 100},
        "tax_amount": {"value": 10},
        "discount": {"value": 0},
        "total_amount": {"value": 120},
        "line_items": []
    })
    assert result["overall_status"] == "FAIL"

def test_pnl_not_applicable_when_fields_missing():
    result = validate_profit_and_loss({})
    assert result["overall_status"] == "NOT_APPLICABLE"

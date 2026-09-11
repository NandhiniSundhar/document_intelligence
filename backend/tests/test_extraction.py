from app.services.extraction_service import extract

def test_pnl_extraction():
    text = """CONSOLIDATED PROFIT AND LOSS ACCOUNT
For the year ended March 31, 2026
Interest earned 348,618.15 336,367.43
Other income 146,847.66 194,548.50
Total 495,462.81 470,915.93
"""
    result = extract(text, "profit_and_loss")
    assert result["document_title"]
    assert result["line_items"]

def test_invoice_extraction():
    text = """Invoice No: INV-100
Invoice Date: 2026-08-15
Vendor: ABC Technologies
Subtotal: USD 100.00
Tax: USD 10.00
Total Amount: USD 110.00"""
    result = extract(text, "invoice")
    assert result["invoice_number"]["value"] == "INV-100"
    assert result["subtotal"]["value"] == 100.0
    assert result["total_amount"]["value"] == 110.0

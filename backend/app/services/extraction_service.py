import re
from typing import Any, Dict, List
from app.schemas.extraction import empty_extraction

MONEY_RE = r"[-(]?\s*[₹$€£]?\s*\d[\d,]*(?:\.\d+)?\s*\)?"

def parse_number(value):
    if value is None:
        return None
    s = str(value).strip()
    negative = s.startswith("(") and s.endswith(")")
    s = s.replace(",", "").replace("₹", "").replace("$", "").replace("€", "").replace("£", "")
    s = s.replace("(", "").replace(")", "").strip()
    try:
        n = float(s)
        return -n if negative else n
    except ValueError:
        return None

def clean_line(s):
    return re.sub(r"\s+", " ", s).strip(" :-\t")

def find_money_values(line):
    vals = re.findall(MONEY_RE, line)
    return [parse_number(v) for v in vals if parse_number(v) is not None]

def detect_currency(text):
    upper = text.upper()
    if "USD" in upper or "$" in text:
        return "USD" if "USD" in upper else "$"
    if "EUR" in upper or "€" in text:
        return "EUR" if "EUR" in upper else "€"
    if "GBP" in upper or "£" in text:
        return "GBP" if "GBP" in upper else "£"
    if "INR" in upper or "₹" in text or "RS." in upper:
        return "INR"
    return None

def first_match(pattern, text, flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None

def generic_statement_parser(text: str, document_type: str) -> Dict[str, Any]:
    data = empty_extraction(document_type)
    data["currency"] = detect_currency(text)
    lines = [clean_line(x) for x in text.splitlines() if clean_line(x)]

    if document_type == "balance_sheet":
        data["document_title"] = first_match(r"(CONSOLIDATED BALANCE SHEET)", text)
        data["statement_period"] = first_match(
            r"(As at [A-Za-z]+ \d{1,2}, \d{4})", text
        )
        data["entity_name"] = first_match(r"\n([A-Z][A-Za-z .&]+ Limited)\s*$", text)
        data["line_items"] = extract_statement_rows(lines)
        data["header_fields"] = extract_headers(lines)
        add_named_values(data, text, {
            "total_assets": [r"^Total\s+([0-9,.\-()]+)", r"\bTotal\s+Assets\b.*?("+MONEY_RE+r")"],
            "total_liabilities": [r"Total\s+Liabilities\b.*?("+MONEY_RE+r")"],
            "total_equity": [r"Total\s+Equity\b.*?("+MONEY_RE+r")"],
        })
    elif document_type == "profit_and_loss":
        data["document_title"] = first_match(r"(CONSOLIDATED PROFIT AND LOSS ACCOUNT)", text)
        data["statement_period"] = first_match(
            r"(For the year ended [A-Za-z]+ \d{1,2}, \d{4})", text
        )
        data["line_items"] = extract_statement_rows(lines)
        data["header_fields"] = extract_headers(lines)
        mapping = {
            "interest_earned": [r"Interest earned\s+(.*)$"],
            "other_income": [r"Other income\s+(.*)$"],
            "total_income": [r"^Total\s+(.*)$"],
            "interest_expended": [r"Interest expended\s+(.*)$"],
            "operating_expenses": [r"Operating expenses,?\s+(.*)$"],
            "provisions_and_contingencies": [r"Provisions and contingencies\s+(.*)$"],
            "total_expenditure": [r"^Total\s+(.*)$"],
            "net_profit_before_minority_interest": [
                r"Consolidated Net Profit for the year before Minority Interest\s+(.*)$"
            ],
            "minority_interest": [r"Less\s*:\s*Minority Interest\s+(.*)$"],
            "net_profit": [
                r"Consolidated Net Profit for the year attributable to the group\s+(.*)$"
            ],
            "basic_eps": [r"Basic\s+(.*)$"],
            "diluted_eps": [r"Diluted\s+(.*)$"],
        }
        add_named_values(data, text, mapping)
    elif document_type == "cash_flow_statement":
        data["document_title"] = first_match(r"(CONSOLIDATED CASH FLOW STATEMENT)", text)
        data["statement_period"] = first_match(
            r"(For the year ended [A-Za-z]+ \d{1,2}, \d{4})", text
        )
        data["line_items"] = extract_statement_rows(lines)
        data["header_fields"] = extract_headers(lines)
        mapping = {
            "operating_cash_flow": [r"Net cash flows from operating activities?\s+(.*)$"],
            "investing_cash_flow": [r"Net cash flow from / \(used.*?investing.*?\s+(.*)$"],
            "financing_cash_flow": [r"Net cash flow from / \(used.*?financing.*?\s+(.*)$"],
            "net_change_in_cash": [r"Net increase.*?cash.*?\s+(.*)$"],
            "opening_cash": [r"Opening Cash.*?\s+(.*)$"],
            "closing_cash": [r"Closing Cash.*?\s+(.*)$"],
        }
        add_named_values(data, text, mapping)
    return data

def extract_headers(lines):
    headers = {}
    for line in lines[:20]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[clean_line(k).lower().replace(" ", "_")] = clean_line(v)
    return headers

def extract_statement_rows(lines):
    rows = []
    stop_words = ("significant accounting", "as per our report", "for and on behalf")
    for line in lines:
        if any(x in line.lower() for x in stop_words):
            continue
        vals = find_money_values(line)
        if vals:
            label = re.sub(MONEY_RE, " ", line)
            label = clean_line(label)
            if len(label) >= 2 and not re.fullmatch(r"[\d\s./-]+", label):
                rows.append({
                    "description": label,
                    "values": vals,
                    "source_text": line
                })
    return rows

def add_named_values(data, text, mapping):
    for key, patterns in mapping.items():
        found = None
        evidence = None
        for pattern in patterns:
            m = re.search(pattern, text, re.I | re.M)
            if m:
                nums = find_money_values(m.group(0))
                if nums:
                    found = nums
                    evidence = m.group(0).strip()
                    break
        if found is not None:
            data[key] = {
                "value": found[0] if len(found) == 1 else found,
                "evidence": evidence,
                "page_number": page_for_evidence(text, evidence),
            }

def page_for_evidence(full_text, evidence):
    if not evidence:
        return None
    before = full_text.split(evidence, 1)[0]
    pages = before.count("[PAGE ")
    return max(1, pages)

def invoice_parser(text: str) -> Dict[str, Any]:
    data = empty_extraction("invoice")
    data["currency"] = detect_currency(text)

    patterns = {
        "invoice_number": [
            r"(?:invoice\s*(?:no|number|#)|inv\.?\s*no\.?)\s*[:#-]?\s*([A-Z0-9][A-Z0-9./_-]+)"
        ],
        "invoice_date": [
            r"(?:invoice\s*date|date)\s*[:#-]?\s*([0-9]{1,4}[/-][0-9]{1,2}[/-][0-9]{2,4})"
        ],
        "vendor_name": [
            r"(?:vendor|seller|supplier|from)\s*[:#-]\s*(.+)"
        ],
        "customer_name": [
            r"(?:customer|buyer|bill\s*to|billed\s*to)\s*[:#-]\s*(.+)"
        ],
        "subtotal": [r"(?:subtotal|sub\s*total)\s*[:#-]?\s*("+MONEY_RE+r")"],
        "tax_amount": [r"(?:tax|gst|vat)\s*[:#-]?\s*("+MONEY_RE+r")"],
        "discount": [r"(?:discount)\s*[:#-]?\s*("+MONEY_RE+r")"],
        "total_amount": [
            r"(?:grand\s*total|total\s*amount|amount\s*due|invoice\s*total|total)\s*[:#-]?\s*("+MONEY_RE+r")"
        ],
    }

    for key, pats in patterns.items():
        for pat in pats:
            m = re.search(pat, text, re.I | re.M)
            if m:
                val = m.group(1).strip()
                parsed = parse_number(val)
                data[key] = {
                    "value": parsed if parsed is not None else val,
                    "evidence": m.group(0).strip(),
                    "page_number": page_for_evidence(text, m.group(0).strip())
                }
                break

    data["line_items"] = parse_invoice_lines(text)
    return data

def parse_invoice_lines(text):
    rows = []
    for line in text.splitlines():
        vals = find_money_values(line)
        if len(vals) >= 2:
            label = clean_line(re.sub(MONEY_RE, " ", line))
            if label and not label.lower().startswith(("total", "subtotal", "tax")):
                rows.append({
                    "description": label,
                    "quantity": vals[0] if len(vals) >= 3 else None,
                    "unit_price": vals[-2] if len(vals) >= 3 else None,
                    "amount": vals[-1],
                    "source_text": clean_line(line),
                })
    return rows

def extract(text: str, document_type: str) -> Dict[str, Any]:
    if document_type == "invoice":
        return invoice_parser(text)
    return generic_statement_parser(text, document_type)

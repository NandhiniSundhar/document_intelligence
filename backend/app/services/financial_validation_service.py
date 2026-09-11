from math import isfinite

TOLERANCE = 0.02

def num(obj):
    if isinstance(obj, dict):
        obj = obj.get("value")
    if isinstance(obj, list):
        return obj[0] if obj else None
    try:
        return float(obj) if obj is not None else None
    except Exception:
        return None

def check(name, formula, operands, calculated, reported):
    if calculated is None or reported is None:
        return {
            "name": name, "formula": formula, "operands": operands,
            "calculated_value": calculated, "reported_value": reported,
            "variance": None, "status": "NOT_APPLICABLE",
            "message": "Required source fields are not available."
        }
    variance = round(calculated - reported, 2)
    status = "PASS" if abs(variance) <= TOLERANCE else "FAIL"
    return {
        "name": name, "formula": formula, "operands": operands,
        "calculated_value": round(calculated, 2),
        "reported_value": round(reported, 2),
        "variance": variance,
        "status": status
    }

def validate_invoice(data):
    s = num(data.get("subtotal"))
    tax = num(data.get("tax_amount"))
    discount = num(data.get("discount")) or 0.0
    total = num(data.get("total_amount"))
    checks = []

    if s is not None and total is not None:
        calc = s + (tax or 0) - discount
        checks.append(check(
            "invoice_total_check",
            "subtotal + tax_amount - discount",
            {"subtotal": s, "tax_amount": tax, "discount": discount},
            calc, total
        ))
    else:
        checks.append(check(
            "invoice_total_check",
            "subtotal + tax_amount - discount",
            {"subtotal": s, "tax_amount": tax, "discount": discount},
            None, total
        ))

    for item in data.get("line_items", []):
        q = num(item.get("quantity"))
        p = num(item.get("unit_price"))
        a = num(item.get("amount"))
        if q is not None and p is not None and a is not None:
            checks.append(check(
                "line_item_quantity_price_check",
                "quantity * unit_price",
                {"quantity": q, "unit_price": p},
                q * p, a
            ))

    return finalize(checks)

def validate_balance_sheet(data):
    # The source can expose many naming variations. We only calculate a check
    # when the actual required fields were extracted.
    assets = num(data.get("total_assets"))
    liabilities = num(data.get("total_liabilities"))
    equity = num(data.get("total_equity"))
    checks = []

    if assets is not None and liabilities is not None and equity is not None:
        checks.append(check(
            "balance_sheet_equation",
            "total_liabilities + total_equity",
            {"total_liabilities": liabilities, "total_equity": equity},
            liabilities + equity, assets
        ))
    else:
        checks.append(check(
            "balance_sheet_equation",
            "total_liabilities + total_equity",
            {"total_liabilities": liabilities, "total_equity": equity},
            None, assets
        ))
    return finalize(checks)

def validate_profit_and_loss(data):
    interest = num(data.get("interest_earned"))
    other = num(data.get("other_income"))
    total_income = num(data.get("total_income"))
    exp1 = num(data.get("interest_expended"))
    exp2 = num(data.get("operating_expenses"))
    exp3 = num(data.get("provisions_and_contingencies"))
    total_exp = num(data.get("total_expenditure"))
    profit_before = num(data.get("net_profit_before_minority_interest"))
    minority = num(data.get("minority_interest"))
    net_profit = num(data.get("net_profit"))

    checks = [
        check("total_income_check", "interest_earned + other_income",
               {"interest_earned": interest, "other_income": other},
               interest + other if interest is not None and other is not None else None,
               total_income),
        check("total_expenditure_check",
               "interest_expended + operating_expenses + provisions_and_contingencies",
               {"interest_expended": exp1, "operating_expenses": exp2,
                "provisions_and_contingencies": exp3},
               exp1 + exp2 + exp3 if None not in (exp1, exp2, exp3) else None,
               total_exp),
        check("net_profit_before_minority_check",
               "total_income - total_expenditure",
               {"total_income": total_income, "total_expenditure": total_exp},
               total_income - total_exp if None not in (total_income, total_exp) else None,
               profit_before),
        check("net_profit_attributable_check",
               "profit_before_minority_interest - minority_interest",
               {"profit_before_minority_interest": profit_before, "minority_interest": minority},
               profit_before - minority if None not in (profit_before, minority) else None,
               net_profit),
    ]
    return finalize(checks)

def validate_cash_flow(data):
    op = num(data.get("operating_cash_flow"))
    inv = num(data.get("investing_cash_flow"))
    fin = num(data.get("financing_cash_flow"))
    net = num(data.get("net_change_in_cash"))
    checks = [
        check("net_cash_change_check",
              "operating_cash_flow + investing_cash_flow + financing_cash_flow",
              {"operating_cash_flow": op, "investing_cash_flow": inv, "financing_cash_flow": fin},
              op + inv + fin if None not in (op, inv, fin) else None,
              net)
    ]
    return finalize(checks)

def finalize(checks):
    failures = [c for c in checks if c["status"] == "FAIL"]
    applicable = [c for c in checks if c["status"] != "NOT_APPLICABLE"]
    overall = "FAIL" if failures else ("PASS" if applicable else "NOT_APPLICABLE")
    return {
        "checks": checks,
        "overall_status": overall,
        "issues": [f"{c['name']}: variance {c['variance']}" for c in failures]
    }

def validate(data, document_type):
    if document_type == "invoice":
        return validate_invoice(data)
    if document_type == "balance_sheet":
        return validate_balance_sheet(data)
    if document_type == "profit_and_loss":
        return validate_profit_and_loss(data)
    return validate_cash_flow(data)

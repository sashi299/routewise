from decimal import Decimal
from typing import Any

from pydantic import ValidationError

from .schema import Invoice


def _close(a: Decimal, b: Decimal, tolerance: Decimal = Decimal("0.02")) -> bool:
    return abs(a - b) <= tolerance


def verify_invoice(source_text: str, candidate: Any) -> dict[str, Any]:
    checks: dict[str, bool] = {"schema": False, "arithmetic": False, "grounding": False}
    errors: list[str] = []
    try:
        invoice = Invoice.model_validate(candidate)
        checks["schema"] = True
    except ValidationError as exc:
        errors.append("schema: " + "; ".join(e["msg"] for e in exc.errors()))
        return {"passed": False, "checks": checks, "errors": errors, "missing_fields": 0}

    amounts = [item.amount for item in invoice.line_items]
    arithmetic = True
    if invoice.subtotal is not None and amounts:
        arithmetic &= _close(sum(amounts, Decimal(0)), invoice.subtotal)
    if invoice.subtotal is not None and invoice.tax is not None and invoice.total is not None:
        arithmetic &= _close(invoice.subtotal + invoice.tax, invoice.total)
    checks["arithmetic"] = arithmetic
    if not arithmetic:
        errors.append("arithmetic consistency failed")

    grounded_values = [invoice.vendor, invoice.invoice_number, invoice.currency]
    grounded_values += [str(invoice.subtotal), str(invoice.tax), str(invoice.total)]
    present = [v for v in grounded_values if v not in (None, "None")]
    checks["grounding"] = all(str(v).lower() in source_text.lower() for v in present)
    if not checks["grounding"]:
        errors.append("one or more scalar values are not grounded in source text")

    required = [invoice.vendor, invoice.invoice_number, invoice.date, invoice.subtotal, invoice.tax, invoice.total, invoice.currency]
    missing = sum(value is None for value in required)
    return {"passed": all(checks.values()), "checks": checks, "errors": errors, "missing_fields": missing, "invoice": invoice.model_dump(mode="json")}

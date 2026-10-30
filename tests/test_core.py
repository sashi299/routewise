import pytest

from routewise.cost import TokenPrice, calculate_cost
from routewise.verifier import verify_invoice


def good_invoice():
    return {"vendor":"Acme", "invoice_number":"INV-1", "date":"2026-01-01", "currency":"USD", "line_items":[{"description":"Widget", "quantity":"2", "unit_price":"5", "amount":"10"}], "subtotal":"10", "tax":"1", "total":"11"}


def test_cost_calculation():
    assert calculate_cost(1_000_000, 500_000, TokenPrice(0.02, 0.06)) == pytest.approx(0.05)


def test_invoice_verifier_passes_grounded_consistent_invoice():
    result = verify_invoice("Acme INV-1 2026-01-01 USD 10 1 11", good_invoice())
    assert result["passed"] is True
    assert all(result["checks"].values())


def test_invoice_verifier_rejects_bad_arithmetic():
    candidate = good_invoice(); candidate["total"] = "999"
    result = verify_invoice("Acme INV-1 2026-01-01 USD 10 1 999", candidate)
    assert result["passed"] is False
    assert result["checks"]["arithmetic"] is False

from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

VENDORS = ["Northstar Supplies", "Acme Industrial", "Blue River Office", "Cedar Labs", "Vertex Logistics"]
ITEMS = ["Consulting hours", "Widget pack", "Support plan", "Cloud usage", "Packaging", "Replacement parts"]
CURRENCIES = [("USD", "$"), ("EUR", "€"), ("GBP", "£"), ("INR", "₹")]


def make_invoice(rng: random.Random, index: int) -> tuple[str, dict]:
    vendor = rng.choice(VENDORS)
    currency, symbol = rng.choice(CURRENCIES)
    inv_date = date(2026, 1, 1) + timedelta(days=rng.randrange(300))
    invoice_number = f"INV-{inv_date.year}-{index:04d}"
    lines = []
    for _ in range(rng.randint(2, 5)):
        quantity = Decimal(rng.randint(1, 12))
        unit_price = Decimal(rng.randint(15, 900)) + Decimal(rng.randint(0, 99)) / 100
        amount = (quantity * unit_price).quantize(Decimal("0.01"))
        lines.append({"description": rng.choice(ITEMS), "quantity": str(quantity), "unit_price": str(unit_price), "amount": str(amount)})
    subtotal = sum(Decimal(item["amount"]) for item in lines).quantize(Decimal("0.01"))
    tax = (subtotal * Decimal(rng.choice(["0", "0.05", "0.08", "0.10", "0.20"]))).quantize(Decimal("0.01"))
    total = subtotal + tax
    truth = {"vendor": vendor, "invoice_number": invoice_number, "date": inv_date.isoformat(), "line_items": lines, "subtotal": str(subtotal), "tax": str(tax), "total": str(total), "currency": currency}
    template = rng.randrange(3)
    if template == 0:
        text = f"{vendor}\nINVOICE {invoice_number}\nInvoice date: {inv_date.isoformat()}\nCurrency: {currency}\n" + "\n".join(f"{x['description']} | {x['quantity']} x {symbol}{x['unit_price']} = {symbol}{x['amount']}" for x in lines) + f"\nSubtotal: {symbol}{subtotal}\nTax: {symbol}{tax}\nTotal: {symbol}{total}"
    elif template == 1:
        text = f"BILL TO: RouteWise Demo\nFROM: {vendor}\nNo. {invoice_number} | Date {inv_date.strftime('%d/%m/%Y')}\n" + "\n".join(f"- {x['description']} ({x['quantity']} units) {symbol}{x['amount']}" for x in lines) + f"\nNET {symbol}{subtotal} | VAT {symbol}{tax} | AMOUNT DUE {symbol}{total}\n{currency}"
    else:
        text = f"{vendor} :: {invoice_number} :: {inv_date.isoformat()} :: {currency}\nITEMS\n" + "\n".join(f"{x['description']} .... {x['amount']}" for x in lines) + f"\nSUB-TOTAL {subtotal}\nTAX {tax}\nGRAND TOTAL {total}"
    if index % 17 == 0:
        text = "PAGE 1 OF 2\n" + text.replace("\nITEMS\n", "\nITEMS\n") + "\nPAGE 2 OF 2\nTerms: payment due in 30 days."
    if index % 23 == 0:
        truth["tax"] = None
        truth["total"] = None
        text += "\nTax and total omitted from supplied copy."
    return text, truth


def generate(output_dir: Path, seed: int = 20261012, count: int = 150) -> None:
    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for index in range(1, count + 1):
        source, truth = make_invoice(rng, index)
        rows.append({"id": index, "source": source, "ground_truth": truth, "split": "train" if index <= 50 else "test"})
    with (output_dir / "invoices.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    for split in ("train", "test"):
        with (output_dir / f"invoices_{split}.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                if row["split"] == split:
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--seed", type=int, default=20261012)
    args = parser.parse_args()
    generate(args.output, args.seed)

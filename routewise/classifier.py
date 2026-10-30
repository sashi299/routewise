from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score

FEATURE_NAMES = ("schema_ok", "arithmetic_ok", "grounding_ok", "output_length", "missing_fields", "self_confidence")


def features_from_verification(result: dict[str, Any], output: dict[str, Any] | None = None) -> list[float]:
    checks = result.get("checks", {})
    return [float(checks.get("schema", False)), float(checks.get("arithmetic", False)), float(checks.get("grounding", False)), float(len(str(output or result.get("invoice", {})))), float(result.get("missing_fields", 0)), float(result.get("self_confidence", 0.5))]


@dataclass
class EscalationClassifier:
    model: LogisticRegression

    @classmethod
    def fit(cls, rows: list[tuple[list[float], int]]) -> EscalationClassifier:
        if len({label for _, label in rows}) < 2:
            raise ValueError("classifier training requires both correct and incorrect examples")
        model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=0)
        model.fit(np.asarray([x for x, _ in rows]), np.asarray([y for _, y in rows]))
        return cls(model)

    def probability_wrong(self, features: list[float]) -> float:
        return float(self.model.predict_proba(np.asarray([features]))[0, 1])

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: Path) -> EscalationClassifier:
        return joblib.load(path)

    def report(self, rows: list[tuple[list[float], int]]) -> dict[str, float]:
        y_true = [label for _, label in rows]
        y_pred = [int(self.probability_wrong(features) >= 0.5) for features, _ in rows]
        return {"precision": float(precision_score(y_true, y_pred, zero_division=0)), "recall": float(recall_score(y_true, y_pred, zero_division=0))}

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPrice:
    input_usd_per_million: float
    output_usd_per_million: float


def calculate_cost(input_tokens: int, output_tokens: int, price: TokenPrice) -> float:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts must be non-negative")
    return (input_tokens * price.input_usd_per_million + output_tokens * price.output_usd_per_million) / 1_000_000

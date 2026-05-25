def optional_str(value) -> str | None:
    return value if isinstance(value, str) else None


def payment_method_label(order, default: str | None = None) -> str | None:
    payment = getattr(order, "payment", None)
    if not payment:
        return default

    card_brand = optional_str(getattr(payment, "card_brand", None))
    card_last4 = optional_str(getattr(payment, "card_last4", None))

    if not card_brand and not card_last4:
        return default
    if card_brand and card_brand.startswith("Kapıda Ödeme"):
        return card_brand
    if card_last4:
        return f"Kredi Kartı (*{card_last4})"
    return card_brand or default

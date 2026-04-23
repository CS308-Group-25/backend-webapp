def process_payment(
    card_number: str, card_last4: str, card_brand: str, amount: float
) -> bool:
    """
    Mock payment processor. Always returns True (success).
    card_number is accepted transiently and never stored or logged.
    Replace with real payment provider integration in production.
    """
    return True

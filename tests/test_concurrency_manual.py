#!/usr/bin/env python3
"""
T-239: Manual concurrency test — two simultaneous checkouts for the last item.

Bypasses the HTTP layer and calls OrderService directly with two real PostgreSQL
sessions in separate threads.  A threading.Barrier synchronises both threads so
they hit place_order at the same instant, forcing them to contend on the
SELECT FOR UPDATE row lock.

Expected outcome
----------------
  - Exactly one thread succeeds (HTTP 201 equivalent).
  - The other is rejected with 409 or 400.
  - Final product stock == 0  (no oversell).

Usage
-----
    python scripts/test_concurrency_manual.py

Requires DATABASE_URL in .env.  The FastAPI server does NOT need to be running.
"""

import os
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

# ── Project root on path ─────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── Stub optional dependency that may not be installed ───────────────────────
# xhtml2pdf is only needed for PDF generation, which is mocked in this test.
_stub = MagicMock()
sys.modules.setdefault("xhtml2pdf", _stub)
sys.modules.setdefault("xhtml2pdf.pisa", _stub)

# ── App imports (after stub) ──────────────────────────────────────────────────
from fastapi import HTTPException  # noqa: E402

from core.database import SessionLocal  # noqa: E402
from modules.auth.model import User  # noqa: E402
from modules.cart.model import Cart, CartItem  # noqa: E402
from modules.cart.repository import CartRepository  # noqa: E402
from modules.orders.model import Order, OrderItem, Payment  # noqa: E402
from modules.orders.repository import OrderRepository  # noqa: E402
from modules.orders.schema import OrderRequest  # noqa: E402
from modules.orders.service import OrderService  # noqa: E402
from modules.products.model import Product  # noqa: E402
from modules.products.repository import ProductRepository  # noqa: E402

# ── Unique tag so test rows are identifiable and safe to delete ───────────────
_TAG = f"conctest_{os.getpid()}"


# ─────────────────────────────────────────────────────────────────────────────
# Setup / teardown helpers
# ─────────────────────────────────────────────────────────────────────────────


def _setup(db) -> tuple[int, list[int]]:
    """
    Insert one product (stock=1) and two users each with a pre-filled cart.
    Returns (product_id, [user_id_a, user_id_b]).
    """
    product = Product(
        name=f"LastItemWidget [{_TAG}]",
        stock=1,
        price=10.00,
        description="Temporary row — created by test_concurrency_manual.py",
    )
    db.add(product)
    db.flush()
    product_id = product.id

    user_ids = []
    for i in range(2):
        user = User(
            name=f"ConcurrencyTestUser{i} [{_TAG}]",
            email=f"{_TAG}_user{i}@test.invalid",
            password_hash="$2b$12$not_a_real_hash_just_a_placeholder",
        )
        db.add(user)
        db.flush()
        user_ids.append(user.id)

        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
        db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=1))

    db.commit()
    return product_id, user_ids


def _teardown(db, product_id: int, user_ids: list[int]) -> None:
    """Remove all rows created by _setup, in FK-safe order."""
    order_ids = [
        row.id
        for uid in user_ids
        for row in db.query(Order).filter(Order.user_id == uid).all()
    ]
    if order_ids:
        db.query(Payment).filter(
            Payment.order_id.in_(order_ids)
        ).delete(synchronize_session=False)
        db.query(OrderItem).filter(
            OrderItem.order_id.in_(order_ids)
        ).delete(synchronize_session=False)
        db.query(Order).filter(
            Order.id.in_(order_ids)
        ).delete(synchronize_session=False)

    cart_ids = [
        row.id
        for uid in user_ids
        for row in db.query(Cart).filter(Cart.user_id == uid).all()
    ]
    if cart_ids:
        db.query(CartItem).filter(
            CartItem.cart_id.in_(cart_ids)
        ).delete(synchronize_session=False)
        db.query(Cart).filter(
            Cart.id.in_(cart_ids)
        ).delete(synchronize_session=False)

    db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
    db.query(Product).filter(Product.id == product_id).delete(synchronize_session=False)
    db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Thread worker
# ─────────────────────────────────────────────────────────────────────────────


def _order_request() -> OrderRequest:
    req = MagicMock(spec=OrderRequest)
    req.card_number = "4111111111111111"
    req.card_last4 = "1111"
    req.card_brand = "Visa"
    req.delivery_address = "1 Concurrency Lane"
    return req


def _run_checkout(
    user_id: int,
    barrier: threading.Barrier,
    results: dict,
    idx: int,
) -> None:
    """
    Open a fresh DB session, build the service stack, then wait at the barrier
    so both threads are released simultaneously into place_order.
    """
    db = SessionLocal()
    try:
        invoice_svc = MagicMock()
        invoice_svc.generate_invoice.return_value = MagicMock(
            invoice_number="INV-CONCTEST", pdf_path=None
        )
        service = OrderService(
            order_repo=OrderRepository(db),
            cart_repo=CartRepository(db),
            product_repo=ProductRepository(db),
            invoice_service=invoice_svc,
        )

        barrier.wait()  # both threads released here at the same instant
        t0 = time.perf_counter()
        service.place_order(user_id=user_id, data=_order_request())
        elapsed = time.perf_counter() - t0
        results[idx] = ("ok", 201, elapsed)

    except HTTPException as exc:
        results[idx] = ("rejected", exc.status_code, exc.detail)
    except Exception as exc:
        results[idx] = ("crash", type(exc).__name__, str(exc))
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Assertion helper
# ─────────────────────────────────────────────────────────────────────────────


def _check(label: str, passed: bool) -> bool:
    mark = "PASS" if passed else "FAIL"
    print(f"  [{mark}] {label}")
    return passed


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    print("\n" + "=" * 60)
    print("  T-239: Concurrent checkout — last item in stock")
    print("=" * 60 + "\n")

    # ── Setup ────────────────────────────────────────────────────────────────
    setup_db = SessionLocal()
    try:
        product_id, user_ids = _setup(setup_db)
    except Exception as exc:
        setup_db.rollback()
        setup_db.close()
        print(f"  SETUP FAILED: {exc}")
        sys.exit(1)
    setup_db.close()

    print(f"  product_id : {product_id}  (stock=1)")
    print(f"  user_ids   : {user_ids}")
    print(f"  Both users have a cart containing 1 unit of product {product_id}\n")

    # ── Concurrent placement ─────────────────────────────────────────────────
    results: dict[int, tuple] = {}
    barrier = threading.Barrier(2)
    threads = [
        threading.Thread(
            target=_run_checkout,
            args=(uid, barrier, results, i),
            daemon=True,
            name=f"checkout-{i}",
        )
        for i, uid in enumerate(user_ids)
    ]

    print("  Firing both checkouts simultaneously …\n")
    with (
        patch("modules.orders.service.process_payment", return_value=True),
        patch("modules.orders.service.send_invoice_email"),
    ):
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

    # ── Print per-thread outcome ──────────────────────────────────────────────
    for i, outcome in sorted(results.items()):
        tag = outcome[0]
        if tag == "ok":
            print(f"  thread-{i} [user {user_ids[i]}]  →  SUCCESS (201)  "
                  f"in {outcome[2]*1000:.1f} ms")
        elif tag == "rejected":
            print(f"  thread-{i} [user {user_ids[i]}]  →  REJECTED "
                  f"(HTTP {outcome[1]}): {outcome[2]}")
        else:
            print(f"  thread-{i} [user {user_ids[i]}]  →  CRASH "
                  f"({outcome[1]}): {outcome[2]}")

    # ── Verify final stock in DB ─────────────────────────────────────────────
    verify_db = SessionLocal()
    final_product = verify_db.query(Product).filter(Product.id == product_id).first()
    final_stock = final_product.stock if final_product else -1
    verify_db.close()
    print(f"\n  Final stock in DB: {final_stock}")

    # ── Teardown ──────────────────────────────────────────────────────────────
    teardown_db = SessionLocal()
    try:
        _teardown(teardown_db, product_id, user_ids)
        print("  Test rows removed from DB\n")
    except Exception as exc:
        teardown_db.rollback()
        print(f"  TEARDOWN WARNING: {exc}\n")
    finally:
        teardown_db.close()

    # ── Assertions ────────────────────────────────────────────────────────────
    print("Assertions")
    print("-" * 40)

    ok_count = sum(1 for o in results.values() if o[0] == "ok")
    rejected_count = sum(
        1 for o in results.values() if o[0] == "rejected" and o[1] in (400, 409)
    )
    crash_count = sum(1 for o in results.values() if o[0] == "crash")

    all_passed = all([
        _check("Exactly one checkout succeeded", ok_count == 1),
        _check("Exactly one checkout rejected (400 or 409)", rejected_count == 1),
        _check("No thread crashed", crash_count == 0),
        _check("Final stock is 0 — no oversell", final_stock == 0),
    ])

    print()
    if all_passed:
        print("ALL CHECKS PASSED\n")
        sys.exit(0)
    else:
        print("ONE OR MORE CHECKS FAILED\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

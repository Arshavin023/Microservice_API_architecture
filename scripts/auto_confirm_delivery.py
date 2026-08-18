#!/usr/bin/env python3
"""
Auto-confirm delivery script.

Finds orders stuck in 'awaiting_confirmation' for more than 2 hours
and automatically marks them as 'delivered'. This is the fallback when
a customer receives their order but forgets (or fails) to confirm.

Flow:
    Staff clicks "Notify customer" → order: awaiting_confirmation
    Customer gets email with "Confirm delivery" button
    If customer clicks → order: delivered (via PATCH /orders/{id}/confirm-delivery)
    If customer ignores for 2hrs → THIS SCRIPT marks it delivered

USAGE:
    python3 scripts/auto_confirm_delivery.py             # dry run
    python3 scripts/auto_confirm_delivery.py --fix       # actually confirms
    python3 scripts/auto_confirm_delivery.py --fix --quiet  # for cron

CRON (every 15 minutes):
    */15 * * * * /path/to/scripts/run_auto_confirm.sh

EXIT CODES:
    0 — no pending confirmations, or all auto-confirmed
    1 — pending found but --fix not passed
    2 — --fix passed but one or more failed
"""
import argparse
import os
import sys
import httpx
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

ORDER_DB_URL = os.getenv(
    "ORDER_DATABASE_URL_SYNC",
    "postgresql://microservices:UcheJudeNnodim3420878321@localhost:5432/order_service_db",
)
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL_LOCAL", "http://localhost:8004")
AUTO_CONFIRM_HOURS = 2


def fetch_stale_orders(conn):
    """Orders stuck in awaiting_confirmation for more than AUTO_CONFIRM_HOURS."""
    cutoff = datetime.utcnow() - timedelta(hours=AUTO_CONFIRM_HOURS)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT id, user_id, updated_at
            FROM orders
            WHERE status = 'awaiting_confirmation'
              AND updated_at < %s
        """, (cutoff,))
        return cur.fetchall()


def auto_confirm(order_id: str, quiet: bool = False) -> bool:
    """
    Calls order-service's internal status update to mark order delivered.
    Uses the same PATCH /orders/{id}/status endpoint used by other workers.
    """
    try:
        resp = httpx.patch(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/status",
            json={"status": "delivered"},
            timeout=10.0,
        )
        if resp.status_code == 200:
            if not quiet:
                print(f"  AUTO-CONFIRMED: order {order_id} → delivered")
            return True
        else:
            if not quiet:
                print(f"  FAILED: order {order_id} (order-service returned {resp.status_code})")
            return False
    except httpx.RequestError as e:
        if not quiet:
            print(f"  FAILED: order {order_id} (unreachable: {e})")
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fix",   action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    conn = psycopg2.connect(ORDER_DB_URL)

    try:
        orders = fetch_stale_orders(conn)

        if not orders:
            if not args.quiet:
                print(f"Auto-confirm: no orders waiting more than {AUTO_CONFIRM_HOURS}hrs for confirmation.")
            sys.exit(0)

        if not args.quiet:
            print(f"Auto-confirm: found {len(orders)} order(s) awaiting confirmation "
                  f"for more than {AUTO_CONFIRM_HOURS} hours:\n")
            for o in orders:
                waiting = datetime.utcnow() - o["updated_at"].replace(tzinfo=None)
                print(f"  order_id={o['id']} (waiting {waiting})")
            print()

        if not args.fix:
            if not args.quiet:
                print("Run with --fix to auto-confirm these orders.")
            sys.exit(1)

        if not args.quiet:
            print("Auto-confirming...\n")

        all_ok = True
        for order in orders:
            if not auto_confirm(str(order["id"]), quiet=args.quiet):
                all_ok = False

        if not args.quiet:
            if all_ok:
                print(f"\nAll {len(orders)} order(s) auto-confirmed.")
            else:
                print(f"\nSome orders could not be auto-confirmed — check logs.")

        sys.exit(0 if all_ok else 2)

    finally:
        conn.close()


if __name__ == "__main__":
    main()

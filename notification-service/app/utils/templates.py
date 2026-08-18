"""
Email templates for all notification types.

Each template returns (subject, html_body, text_body) so the sender
can send multipart emails with both HTML and plain-text fallback.
"""


def payment_succeeded(order_id: str, amount: str) -> tuple[str, str, str]:
    subject = "✅ Payment confirmed — your order is being prepared!"
    html = f"""
<div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:24px">
  <h2 style="color:#ea580c">Payment confirmed 🍕</h2>
  <p>Great news! Your payment of <strong>₦{amount}</strong> has been confirmed.</p>
  <p>Your order <code style="background:#f3f4f6;padding:2px 6px;border-radius:4px">{order_id[:8]}…</code>
     is now being prepared in the kitchen.</p>
  <p>We'll email you again as soon as it's on the way.</p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="color:#6b7280;font-size:13px">Pizzasale — fresh from the oven.</p>
</div>
"""
    text = (
        f"Payment confirmed!\n\n"
        f"Your payment of ₦{amount} for order {order_id[:8]}… has been confirmed.\n"
        f"Your order is now being prepared in the kitchen.\n\n"
        f"We'll email you again when it's on the way.\n\n"
        f"— Pizzasale"
    )
    return subject, html, text


def payment_failed(order_id: str) -> tuple[str, str, str]:
    subject = "❌ Payment failed — please try again"
    html = f"""
<div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:24px">
  <h2 style="color:#dc2626">Payment failed</h2>
  <p>Unfortunately your payment for order
     <code style="background:#f3f4f6;padding:2px 6px;border-radius:4px">{order_id[:8]}…</code>
     did not go through.</p>
  <p>Please try placing a new order and using a different payment method.</p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="color:#6b7280;font-size:13px">Pizzasale — fresh from the oven.</p>
</div>
"""
    text = (
        f"Payment failed\n\n"
        f"Your payment for order {order_id[:8]}… did not go through.\n"
        f"Please try placing a new order and using a different payment method.\n\n"
        f"— Pizzasale"
    )
    return subject, html, text


def shipment_dispatched(
    order_id: str,
    driver_name: str | None,
    driver_phone: str | None,
    delivery_address: str,
) -> tuple[str, str, str]:
    subject = "🛵 Your order is on the way!"
    driver_info = ""
    if driver_name or driver_phone:
        driver_info = "<p>Your driver: "
        if driver_name:
            driver_info += f"<strong>{driver_name}</strong>"
        if driver_phone:
            driver_info += f" — <a href='tel:{driver_phone}'>{driver_phone}</a>"
        driver_info += "</p>"

    html = f"""
<div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:24px">
  <h2 style="color:#ea580c">On the way! 🛵</h2>
  <p>Your order <code style="background:#f3f4f6;padding:2px 6px;border-radius:4px">{order_id[:8]}…</code>
     has been picked up and is heading to you.</p>
  {driver_info}
  <p>Delivering to: <strong>{delivery_address}</strong></p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="color:#6b7280;font-size:13px">Pizzasale — fresh from the oven.</p>
</div>
"""
    driver_line = ""
    if driver_name:
        driver_line = f"Driver: {driver_name}"
        if driver_phone:
            driver_line += f" ({driver_phone})"
        driver_line += "\n"

    text = (
        f"Your order is on the way!\n\n"
        f"Order {order_id[:8]}… has been picked up and is heading to you.\n"
        f"{driver_line}"
        f"Delivering to: {delivery_address}\n\n"
        f"— Pizzasale"
    )
    return subject, html, text


def delivery_pending_confirmation(order_id: str) -> tuple[str, str, str]:
    subject = "📦 Did you receive your order? Please confirm"
    html = f"""
<div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:24px">
  <h2 style="color:#1A1A2E">Did you receive your order? 📦</h2>
  <p>Our rider has reported that your order
     <code style="background:#f3f4f6;padding:2px 6px;border-radius:4px">{order_id[:8]}…</code>
     has been delivered.</p>
  <p>Please log in to confirm you received it. If you don't confirm within
     <strong>2 hours</strong>, your order will be automatically marked as delivered.</p>
  <a href="http://localhost:3000/orders/{order_id}"
     style="display:inline-block;background:#FF6B35;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:12px">
    Confirm delivery
  </a>
  <p style="color:#9ca3af;font-size:13px;margin-top:16px">
    If you did <strong>not</strong> receive your order, please contact us immediately.
  </p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="color:#6b7280;font-size:13px">Pizzasale — fresh Nigerian flavours.</p>
</div>
"""
    text = (
        f"Did you receive your order?\n\n"
        f"Our rider has reported that order {order_id[:8]}… has been delivered.\n"
        f"Please confirm receipt at http://localhost:3000/orders/{order_id}\n\n"
        f"If you don't confirm within 2 hours, your order will be auto-confirmed.\n"
        f"If you did NOT receive it, contact us immediately.\n\n"
        f"— Pizzasale"
    )
    return subject, html, text

def shipment_delivered(order_id: str) -> tuple[str, str, str]:
    subject = "🎉 Your order has been delivered!"
    html = f"""
<div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:24px">
  <h2 style="color:#16a34a">Delivered! 🎉</h2>
  <p>Your order <code style="background:#f3f4f6;padding:2px 6px;border-radius:4px">{order_id[:8]}…</code>
     has been delivered. Enjoy your pizza!</p>
  <p>Thanks for ordering with Pizzasale. We hope to see you again soon.</p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="color:#6b7280;font-size:13px">Pizzasale — fresh from the oven.</p>
</div>
"""
    text = (
        f"Your order has been delivered!\n\n"
        f"Order {order_id[:8]}… has been delivered. Enjoy your pizza!\n\n"
        f"Thanks for ordering with Pizzasale.\n\n"
        f"— Pizzasale"
    )
    return subject, html, text

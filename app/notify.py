import logging
import os

import requests

logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 2
TIMEOUT_SECONDS = 5


def build_message(item) -> str:
    if item.qty == 0:
        return f"Sin stock: {item.name}"
    return f"Stock bajo: {item.name} ({item.qty} unidades)"


def notify_low_stock(item) -> bool:
    url = os.getenv("NOTIFY_WEBHOOK_URL")
    if not url:
        return False

    payload = {
        "event": "low_stock",
        "item_id": item.id,
        "name": item.name,
        "qty": item.qty,
        "text": build_message(item),
    }
    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("No se pudo enviar el aviso de stock bajo: %s", exc)
        return False
    return True

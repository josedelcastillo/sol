from dataclasses import dataclass

from app.config import INVENTORY_API_KEY


@dataclass
class Item:
    id: int
    name: str
    qty: int


class ItemNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


_INITIAL_ITEMS = [
    Item(id=1, name="Laptop", qty=5),
    Item(id=2, name="Monitor", qty=8),
    Item(id=3, name="Teclado", qty=12),
]

_items: dict[int, Item] = {}


def reset() -> None:
    _items.clear()
    for item in _INITIAL_ITEMS:
        _items[item.id] = Item(id=item.id, name=item.name, qty=item.qty)


def list_items() -> list[Item]:
    return list(_items.values())


def withdraw(item_id: int, qty: int) -> Item:
    item = _items.get(item_id)
    if item is None:
        raise ItemNotFoundError(item_id)
    if qty >= item.qty:
        raise InsufficientStockError(f"Stock insuficiente: disponible {item.qty}")
    item.qty -= qty
    return item


def api_key_configured() -> bool:
    return bool(INVENTORY_API_KEY)


reset()

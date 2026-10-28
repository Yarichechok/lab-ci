import pytest

from shop.cart import Cart

class StubRateProvider:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def get_rate(self, currency: str) -> float:
        return self.rate

def test_empty_cart_has_zero_items() -> None:
    cart = Cart()

    assert cart.items_count() == 0


def test_add_single_item() -> None:
    cart = Cart()

    cart.add("book", price=200.0)

    assert cart.items_count() == 1


def test_add_item_with_quantity() -> None:
    cart = Cart()

    cart.add("book", price=200.0, qty=3)

    assert cart.items_count() == 3


def test_add_same_name_increases_quantity() -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=1)

    cart.add("book", price=200.0, qty=2)

    assert cart.items_count() == 3


def test_add_same_name_keeps_original_price() -> None:
    cart = Cart()
    cart.add("book", price=200.0)

    cart.add("book", price=500.0)

    assert cart.items_count() == 2
    assert cart.total() == 400.0


def test_fixture_contains_six_items(cart_with_items: Cart) -> None:
    assert cart_with_items.items_count() == 6

@pytest.mark.parametrize(
    ("discount", "expected"),
    [
        (0, 400.0),
        (10, 360.0),
        (50, 200.0),
        (100, 0.0),
    ],
)
def test_total_with_discount(discount: float, expected: float) -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=2)

    assert cart.total(discount_percent=discount) == expected


def test_add_negative_price_raises() -> None:
    cart = Cart()

    with pytest.raises(ValueError, match="price"):
        cart.add("book", price=-1.0)


def test_add_zero_quantity_raises() -> None:
    cart = Cart()

    with pytest.raises(ValueError, match="qty"):
        cart.add("book", price=200.0, qty=0)


@pytest.mark.parametrize("discount", [-1.0, 101.0])
def test_invalid_discount_raises(discount: float) -> None:
    cart = Cart()

    with pytest.raises(ValueError, match="discount_percent"):
        cart.total(discount_percent=discount)


def test_remove_missing_item_raises() -> None:
    cart = Cart()

    with pytest.raises(KeyError):
        cart.remove("missing")


def test_remove_existing_item() -> None:
    cart = Cart()
    cart.add("book", price=200.0)

    cart.remove("book")

    assert cart.items_count() == 0


def test_total_in_converts_currency() -> None:
    cart = Cart()
    cart.add("book", price=400.0)
    rates = StubRateProvider(rate=40.0)

    result = cart.total_in("USD", rates)

    assert result == 10.0


@pytest.mark.parametrize("rate", [0.0, -1.0])
def test_total_in_invalid_rate_raises(rate: float) -> None:
    cart = Cart()
    cart.add("book", price=400.0)
    rates = StubRateProvider(rate=rate)

    with pytest.raises(ValueError, match="rate"):
        cart.total_in("USD", rates)


def test_most_expensive_empty_cart_returns_none() -> None:
    cart = Cart()

    assert cart.most_expensive() is None


def test_most_expensive_returns_item_with_highest_price() -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=2)
    cart.add("pen", price=15.0, qty=4)

    result = cart.most_expensive()

    assert result is not None
    assert result.name == "book"
    assert result.price == 200.0
    assert result.qty == 2
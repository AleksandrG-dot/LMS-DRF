import stripe

from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_product(product_name):
    """Создает продукт в Stripe."""

    return stripe.Product.create(name=product_name)


def create_stripe_price(product_name, amount):
    """Создает цену в Stripe."""

    return stripe.Price.create(
        currency="rub",
        unit_amount=amount * 100,
        product=product_name.get("id"),
    )


def create_stripe_session(price):
    """Создает сессию на оплату в Stripe."""

    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")

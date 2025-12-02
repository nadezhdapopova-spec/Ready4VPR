import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(name: str):
    """Создает сессию товара в stripe"""
    product = stripe.Product.create(name=name)
    return product.get("id")


def create_stripe_price(product_id: str, amount: int):
    """Создает сессию цены в stripe"""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency="rub",
    )
    return price.get("id")


def create_checkout_session(price_id: str, payment_id: int):
    """Создает сессию оплаты в stripe"""
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        success_url=f"http://localhost:8000/payment/",
        cancel_url=f"http://localhost:8000/payment/",
    )
    return session.get("id"), session.get("url")


def get_session_status(session_id: str):
    """Возвращает статус сессии в stripe"""
    session = stripe.checkout.Session.retrieve(session_id)
    return session.get("payment_status")

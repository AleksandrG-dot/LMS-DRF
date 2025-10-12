import stripe

from config.settings import STRIPE_API_KEY
from users.models import Payment, PaymentCourseStripe

# Настройка ключа
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


def check_stripe_payment():
    """Проверяет указанные платежи Stripe на статус оплаты и вносит изменения в Payment и PaymentCourseStripe"""

    # Получаем все неоплаченные записи PaymentCourseStripe
    stripe_payments = PaymentCourseStripe.objects.filter(is_paid=False)

    results = {"checked": 0, "paid_count": 0, "paid": [], "errors": []}

    for stripe_payment in stripe_payments:
        if not stripe_payment.session_id:
            results["errors"].append(
                f"Отсутствует session_id для платежа {stripe_payment.id}"
            )
            continue

        try:
            # Получаем информацию о сессии из Stripe
            session = stripe.checkout.Session.retrieve(stripe_payment.session_id)
            results["checked"] += 1

            # Проверяем статус оплаты
            if session.payment_status == "paid":
                # Создаем запись в основной модели Payment
                Payment.objects.create(
                    user=stripe_payment.user,
                    date=stripe_payment.date,
                    course=stripe_payment.course,
                    amount=stripe_payment.amount,
                    payment_method="transfer",
                )

                # Обновляем статус в PaymentCourseStripe
                stripe_payment.is_paid = True
                stripe_payment.save()

                results["paid_count"] += 1
                results["paid"].append(stripe_payment.id)

        except stripe.error.StripeError as e:
            results["errors"].append(
                f"Ошибка Stripe для session_id {stripe_payment.session_id}: {str(e)}"
            )
        except Exception as e:
            results["errors"].append(
                f"Общая ошибка для session_id {stripe_payment.session_id}: {str(e)}"
            )

    return results

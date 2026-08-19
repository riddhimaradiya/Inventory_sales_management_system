from decimal import Decimal
from django.db import transaction
from customers.models import Customer
from products.models import Product,StockMovement
from .models import Order, OrderItem
from payments.services import PaymentService

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(customer_id, items):
        customer = (
            Customer.objects
            .select_for_update()
            .filter(id=customer_id,is_active=True)
            .first()
        )
        if not customer:
            raise ValueError("Active customer not found.")
        product_ids = [
            item["product_id"]
            for item in items
        ]
        products = (
            Product.objects
            .select_for_update()
            .filter(id__in=product_ids,is_active=True).order_by("id")
        )
        product_map = {
            product.id: product
            for product in products
        }
        if len(product_map) != len(product_ids):
            raise ValueError(
                "One or more products are not available."
            )
        order=Order.objects.create(
            customer=customer,
            status=Order.OrderStatus.PENDING,
            payment_status=(Order.PaymentStatus.PENDING),
        )
        total_amount = Decimal("0.00")
        order_items = []
        for item in items:
            product = product_map[item["product_id"]]
            quantity = item["quantity"]
            if product.quantity < quantity:
                raise ValueError(
                    f"Insufficient stock for "
                    f"product '{product.name}'. "
                    f"Available: {product.quantity}, "
                    f"Requested: {quantity}."
                )
            unit_price = product.price
            product_amount = (unit_price * quantity)
            gst_percentage = product.gst_percentage
            gst_amount = (product_amount * gst_percentage / Decimal("100"))
            subtotal = (product_amount + gst_amount)
            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    gst_percentage=gst_percentage,
                    gst_amount=gst_amount,
                    subtotal=subtotal,
                )
            )
            total_amount += subtotal

        OrderItem.objects.bulk_create(order_items)
        order.total_amount = total_amount
        order.save(update_fields=["total_amount", "updated_at",])   
        payment = PaymentService.make_payment(
            order=order,
            amount=total_amount,
        )
        if payment.status == (payment.PaymentStatus.FAILED):
            order.status = (Order.OrderStatus.CANCELLED)
            order.payment_status = (Order.PaymentStatus.FAILED)
            order.save(
                update_fields = ["status", "payment_status", "updated_at", ]
            )
            return order

        #Payment successful.
        #Stock deduction happens below.
        for item in order_items:
            product = product_map[item.product_id]
            old_quantity = product.quantity
            product.quantity = (product.quantity - item.quantity)
            product.save(
                update_fields=["quantity", "updated_at",]
            )

            StockMovement.objects.create(
                product=product,
                Movement_Type=StockMovement.MovementType.SALE,
                quantity=item.quantity,
                reference=order.order_number,
                note=f"Sale for order {order.order_number}",
            )
            order.status = (Order.OrderStatus.CONFIRMED)
            order.payment_status = (Order.PaymentStatus.SUCCESS)
            order.save(
                update_fields=["status", "payment_status", "updated_at",]
            )
            return order
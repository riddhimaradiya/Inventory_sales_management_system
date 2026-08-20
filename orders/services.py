from decimal import Decimal
from django.db import transaction
from customers.models import Customer
from products.models import Product,StockMovement
from .models import Order, OrderItem
from payments.services import PaymentService
from products.alert_service import ThresholdAlertService
from notifications.order_notifications import (OrderNotificationService)

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(customer_id, items):

        customer = Customer.objects.get(id=customer_id, is_active=True)
        items_data = items

#Validate and lock products
        product_ids = [
            item["product_id"]
            for item in items_data
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

#Calculate order amount
        subtotal = Decimal("0.00")
        gst_amount = Decimal("0.00")
        validated_items = []
        for item_data in items_data:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]
            if quantity <= 0:
                raise ValueError(
                    "Quantity must be greater than zero."
                )

            product = product_map[product_id]

            #stock validation
            if product.quantity < quantity:
                raise ValueError(
                    f"Insufficient stock for "
                    f"{product.name}."
                )
            item_subtotal = (product.price * quantity)
            item_gst = (
                item_subtotal * product.gst_percentage / Decimal("100")
            )
            subtotal += item_subtotal
            gst_amount += item_gst

            validated_items.append({
                "product": product,
                "quantity": quantity,
                "unit_price": product.price,
                "gst_percentage": product.gst_percentage,
                "item_subtotal": item_subtotal,
                "item_gst": item_gst,
            })

        total_amount = (
            subtotal + gst_amount
        )

#Create Order
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            status=Order.OrderStatus.PENDING,
            payment_status=(
                Order.PaymentStatus.PENDING
            ),
        )

#Create Order Items
        for item in validated_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                gst_percentage=item["gst_percentage"],
                gst_amount=item["item_gst"],
                subtotal=item["item_subtotal"],
            )
#Payment
        payment = PaymentService.make_payment(
            order=order,
            amount=total_amount,
        )

#Payment Failed
        if payment.status != payment.PaymentStatus.SUCCESS:
            order.status = (Order.OrderStatus.CANCELLED)
            order.payment_status = (Order.PaymentStatus.FAILED)
            order.save(
                update_fields=["status","payment_status","updated_at",]
            )
            transaction.on_commit(
                lambda: (
                    OrderNotificationService.send_payment_failed(order, validated_items) 
                ),
                robust=True
            )
            return order

#payment Successful
        threshold_product = []
        for item in validated_items:
            product = item["product"]
            quantity = item["quantity"]
            product.quantity = (product.quantity - quantity)
            product.save(
                update_fields=["quantity","updated_at",]
            )

#stock movement
            StockMovement.objects.create(
                product=product,
                Movement_Type=(StockMovement.MovementType.SALE),
                quantity=quantity,
                reference=(order.order_number),
            )

#Threshold check
            if(product.quantity <= product.threshold_quantity):
                threshold_product.append(product)

#Update Order Status
        order.status = (Order.OrderStatus.CONFIRMED)
        order.payment_status = (Order.PaymentStatus.SUCCESS)
        order.save(
            update_fields=["status","payment_status","updated_at",]
        )

#Customer Whatsapp Norification
        transaction.on_commit(
            lambda:(
                OrderNotificationService.send_order_confirmation(order),
            ),
        robust=True
        )

#Admin Low Stock Alert
        for product in threshold_product:
            transaction.on_commit(
                lambda product=product: (
                    ThresholdAlertService
                    .send_threshold_alert(order,product)
                ),
                robust=True
            )

#Return Order
        return order

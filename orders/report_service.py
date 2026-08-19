import csv
from io import StringIO

class OrderCSVReportService:

    @staticmethod
    def generate_order_csv(order):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "name", "productname", "count",])
        for item in(order.items.select_related("product").all()):
            writer.writerow([
                order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                order.customer.name,
                item.product.name,
                item.quantity,
            ])
        return output.getvalue()
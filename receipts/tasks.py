from celery import shared_task
from receipts.models import Billing


@shared_task
def generate_receipt_pdf(billing_id):

    billing = Billing.objects.get(id=billing_id)

    # Example logic (you can replace with reportlab/weasyprint)
    pdf_url = f"/media/receipts/{billing.transaction_id}.pdf"

    billing.pdf_file = pdf_url
    billing.save()

    return pdf_url
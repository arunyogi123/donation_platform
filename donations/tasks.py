from celery import shared_task
from django.utils import timezone
from uuid import uuid4

from donations.models import Donation, RecurringDonation, PaymentType
from receipts.models import Billing, BillingStatus, PaymentMethod


@shared_task(name="donations.tasks.process_recurring_donations")
def process_recurring_donations():

    due_plans = RecurringDonation.objects.filter(
        is_active=True,
        is_processing=False,
        next_run__lte=timezone.now(),
    )

    for plan in due_plans:
        plan.is_processing = True
        plan.save()

        payment_success = True  # ← hardcoded for testing

        if payment_success:
            # 1. Create donation
            donation = Donation.objects.create(
                donor=plan.donor,
                campaign=plan.campaign,
                amount=plan.amount,
                currency=plan.currency,
                is_anonymous=plan.is_anonymous,
                payment_status=PaymentType.SUCCESS,
            )

            # 2. Create billing ONLY on success
            Billing.objects.create(
                donation=donation,
                recurring_donation=plan,
                transaction_id=str(uuid4()),
                amount=plan.amount,
                currency=plan.currency,
                payment_method=PaymentMethod.KHALTI,
                status=BillingStatus.SUCCESS,
                is_recurring=True,
            )

            # 3. Save history + advance next_run
            plan.mark_success()

        else:
            # Payment failed or pending — release lock, retry next cycle
            plan.is_processing = False
            plan.last_payment_status = PaymentType.FAILURE
            plan.save()
from celery import shared_task
from django.utils import timezone
from uuid import uuid4

from donations.models import Donation, RecurringDonation, PaymentType
from receipts.models import Billing, BillingStatus, PaymentMethod


# =============================================
# BEAT CALLS THIS EVERY 10 SECONDS
# Finds all due plans and processes them
# =============================================
@shared_task(name="donations.tasks.process_recurring_donations")
def process_recurring_donations():

    due_plans = RecurringDonation.objects.filter(
        is_active=True,
        is_processing=False,
        next_run__lte=timezone.now(),
    )

    for plan in due_plans:

        # Mark as processing so it won't be picked up again
        plan.is_processing = True
        plan.save()

        # Simulate payment — in real life this comes from payment gateway
        payment_status = PaymentType.PENDING

        if payment_status == PaymentType.SUCCESS:

            # Create donation record
            donation = Donation.objects.create(
                donor=plan.donor,
                campaign=plan.campaign,
                amount=plan.amount,
                currency=plan.currency,
                is_anonymous=plan.is_anonymous,
                payment_status=PaymentType.SUCCESS,
            )

            # Create billing record
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

            # Save history + advance next_run (defined in model)
            plan.mark_success()

        elif payment_status == PaymentType.FAILURE:
            # No billing, no history
            plan.mark_failure()

        elif payment_status == PaymentType.PENDING:
            # No billing, no history
            plan.is_processing = False
            plan.save()
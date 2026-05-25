from celery import shared_task
from django.db import transaction
from uuid import uuid4

from donations.models import Donation, RecurringDonation, PaymentType
from receipts.models import Billing, BillingStatus, PaymentMethod


@shared_task(name="donations.tasks.process_recurring_donations")
def process_payment(donation_id=None, recurring_id=None, payment_status=PaymentType.SUCCESS):

    with transaction.atomic():

        # =====================================
        # ONE-TIME DONATION
        # =====================================
        if donation_id:

            donation = Donation.objects.select_related("campaign").get(id=donation_id)

            if payment_status == PaymentType.SUCCESS:

                donation.payment_status = PaymentType.SUCCESS
                donation.save()  # ✅ Donation.save() already updates campaign.current_raised

                Billing.objects.create(
                    donation=donation,
                    transaction_id=str(uuid4()),
                    amount=donation.amount,
                    currency=donation.currency,
                    payment_method=PaymentMethod.KHALTI,
                    status=BillingStatus.SUCCESS,
                    is_recurring=False,
                )

            else:

                donation.payment_status = PaymentType.FAILURE
                donation.save()

                Billing.objects.create(
                    donation=donation,
                    transaction_id=str(uuid4()),
                    amount=donation.amount,
                    currency=donation.currency,
                    payment_method=PaymentMethod.KHALTI,
                    status=BillingStatus.FAILED,
                    is_recurring=False,
                )

        # =====================================
        # RECURRING DONATION
        # =====================================
        elif recurring_id:

            plan = RecurringDonation.objects.select_related("campaign", "donor").get(id=recurring_id)

            if payment_status == PaymentType.SUCCESS:

                # ✅ Create the donation record
                donation = Donation.objects.create(
                    donor=plan.donor,
                    campaign=plan.campaign,
                    amount=plan.amount,
                    currency=plan.currency,
                    payment_status=PaymentType.SUCCESS,
                    # ⚠️ set this BEFORE save so Donation.save() does NOT double-update campaign
                )

                # ✅ mark_success() handles: History + campaign.current_raised + next_run + last_run + is_processing
                plan.mark_success()

                # ✅ Billing stored only on SUCCESS
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

            else:
                # ✅ FAILURE: nothing stored in Billing or History
                plan.mark_failure()  # handles: last_payment_status + is_processing + save
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render

from receipts.models import Billing, BillingStatus, PaymentMethod
from donations.models import Donation, RecurringDonation, PaymentType
from payments.utils import KhaltiPayment


# ── ONE TIME DONATION ──────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def initiate_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user)

    if donation.payment_status == PaymentType.SUCCESS:
        return Response({"error": "Already paid"}, status=400)

    data = KhaltiPayment.initiate_payment(
        amount=donation.amount,
        donation_id=donation.id,
        name=request.user.username,
        email=request.user.email,
        phone=getattr(request.user, "phone", "9800000000"),
    )

    return Response({"payment_url": data.get("payment_url")})


@api_view(["GET"])
def donation_callback(request):
    pidx = request.GET.get("pidx")
    donation_id = request.GET.get("purchase_order_id")
    status_param = request.GET.get("status")

    donation = get_object_or_404(Donation, id=donation_id)

    context = {
        "transaction_id": pidx,
        "amount": donation.amount,
    }

    if Billing.objects.filter(transaction_id=pidx).exists():
        return render(request, "payment/index.html", {**context, "status": "success"})

    if status_param and status_param.lower() == "user canceled":
        donation.payment_status = PaymentType.FAILURE
        donation.save()
        return render(request, "payment/index.html", {**context, "status": "cancelled"})

    response = KhaltiPayment.verify_payment(pidx)

    if response.get("status") == "Completed":
        donation.payment_status = PaymentType.SUCCESS
        donation.save()
        Billing.objects.create(
            donation=donation,
            transaction_id=pidx,
            amount=donation.amount,
            currency=donation.currency,
            status=BillingStatus.SUCCESS,
            payment_method=PaymentMethod.KHALTI,
            is_recurring=False,
        )
        return render(request, "payment/index.html", {**context, "status": "success"})

    donation.payment_status = PaymentType.FAILURE
    donation.save()
    return render(request, "payment/index.html", {**context, "status": "failed"})


# ── RECURRING DONATION ─────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def initiate_recurring(request, recurring_id):
    plan = get_object_or_404(RecurringDonation, id=recurring_id, donor=request.user)

    if not plan.is_active:
        return Response({"error": "Recurring plan is not active"}, status=400)

    if plan.is_processing:
        return Response({"error": "Payment already in progress"}, status=400)

    plan.is_processing = True
    plan.save()

    data = KhaltiPayment.initiate_payment(
        amount=plan.amount,
        donation_id=plan.id,
        return_url="http://127.0.0.1:8000/api/payments/recurring/callback/",
        name=request.user.username,
        email=request.user.email,
        phone=request.user.phone or "9800000000",
    )

    return Response({"payment_url": data.get("payment_url")})


@api_view(["GET"])
def recurring_callback(request):
    pidx = request.GET.get("pidx")
    recurring_id = request.GET.get("purchase_order_id")
    status_param = request.GET.get("status")

    plan = get_object_or_404(RecurringDonation, id=recurring_id)

    context = {
        "transaction_id": pidx,
        "amount": plan.amount,
    }

    if Billing.objects.filter(transaction_id=pidx).exists():
        return render(request, "payment/index.html", {**context, "status": "success"})

    if status_param and status_param.lower() == "user canceled":
        plan.last_payment_status = PaymentType.FAILURE
        plan.save()
        return render(request, "payment/index.html", {**context, "status": "cancelled"})

    response = KhaltiPayment.verify_payment(pidx)

    if response.get("status") == "Completed":
        donation = Donation.objects.create(
            donor=plan.donor,
            campaign=plan.campaign,
            amount=plan.amount,
            currency=plan.currency,
            is_anonymous=plan.is_anonymous,
            payment_status=PaymentType.SUCCESS,
        )
        Billing.objects.create(
            donation=donation,
            recurring_donation=plan,
            transaction_id=pidx,
            amount=plan.amount,
            currency=plan.currency,
            status=BillingStatus.SUCCESS,
            payment_method=PaymentMethod.KHALTI,
            is_recurring=True,
        )
        plan.mark_success()
        return render(request, "payment/index.html", {**context, "status": "success"})

    plan.mark_failure()
    return render(request, "payment/index.html", {**context, "status": "failed"})

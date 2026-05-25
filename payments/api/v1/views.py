import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render


from receipts.models import Billing, BillingStatus
from donations.models import Donation,PaymentType
from payments.utils import KhaltiPayment


@api_view(['GET'])
def get_payment_url_by_id(request, id):
    billing = get_object_or_404(Billing, id=id)

    donation = billing.donation or billing.recurring_donation
    donor = donation.donor

    try:
        data = KhaltiPayment.initiate_payment(
            amount=billing.amount,
            donation_id=donation.id,
            name=donor.username,
            email=donor.email,
            phone=getattr(donor, 'phone', '9800000000'),  # ✅ use donor phone if exists
        )
    except requests.Timeout:
        return Response({"error": "Khalti request timed out"}, status=504)
    except requests.RequestException as e:
        return Response({"error": f"Payment initiation failed: {str(e)}"}, status=500)

    pidx = data.get("pidx")

    if not pidx:
        return Response({"error": "No pidx returned from Khalti", "details": data}, status=400)

    billing.transaction_id = pidx
    billing.status = BillingStatus.PENDING
    billing.save()

    return Response({
        "payment_url": data.get("payment_url"),
        "pidx": pidx
    })


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
import requests



from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
import requests




@api_view(['GET'])
def callback_khalti(request):

    pidx = request.GET.get("pidx")
    status_param = request.GET.get("status")

    if not pidx:
        return Response({"error": "Missing pidx"}, status=400)

    billing = Billing.objects.filter(transaction_id=pidx).first()

    if not billing:
        return Response({"error": "Invalid pidx"}, status=404)

    # ❗ HANDLE CANCEL FIRST (NO API CALL)
    if status_param and status_param.lower() == "user canceled":
        billing.status = BillingStatus.FAILED
        billing.save()

        return render(request, "payment/index.html", {
            "status": "cancelled",
            "pidx": pidx,
        })

    # 🔥 VERIFY PAYMENT
    try:
        response = KhaltiPayment.verify_payment(pidx)
        print("KHALTI RESPONSE:", response)

    except requests.Timeout:
        billing.status = BillingStatus.FAILED
        billing.save()
        return Response({"error": "Timeout"}, status=504)

    except requests.RequestException as e:
        billing.status = BillingStatus.FAILED
        billing.save()
        return Response({"error": str(e)}, status=500)

    # 🔥 SUCCESS CHECK
    is_success = response.get("status") == "Completed"

    if is_success:

        # 1️⃣ Update billing
        billing.status = BillingStatus.SUCCESS
        billing.save()

        # 2️⃣ Update donation (THIS triggers campaign update automatically)
        donation = billing.donation

        if donation:
            donation.payment_status = PaymentType.SUCCESS
            donation.save()   # 🔥 IMPORTANT LINE

        return render(request, "payment/index.html", {
            "status": "success",
            "amount": billing.amount,
            "pidx": pidx,
        })

    else:

        billing.status = BillingStatus.FAILED
        billing.save()

        return render(request, "payment/index.html", {
            "status": "failed",
            "pidx": pidx,
        })
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from receipts.models import Billing
from .serializers import BillingSerializer


@api_view(['GET'])
def billing_detail(request, id):

    billing = get_object_or_404(Billing, id=id)

    serializer = BillingSerializer(
        billing,
        context={"request": request}
    )

    return Response(serializer.data)

from django.db.models import Q

@api_view(['GET'])
def billing_list(request):
    if request.user.is_authenticated and not request.user.is_staff:
        billings = Billing.objects.filter(
            Q(donation__donor=request.user) | Q(recurring_donation__donor=request.user)
        ).order_by('-id')
    else:
        billings = Billing.objects.all().order_by('-id')

    serializer = BillingSerializer(
        billings,
        many=True,
        context={"request": request}
    )
    return Response(serializer.data)
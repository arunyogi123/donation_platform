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

@api_view(['GET'])
def billing_list(request):

    billings = Billing.objects.all().order_by('-id')

    serializer = BillingSerializer(
        billings,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)
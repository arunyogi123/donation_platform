from donations.models import Donation, RecurringDonation
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import GenericAPIView
from donations.api.v1.serializers import DonationSerializer, RecurringSerializer
from rest_framework.permissions import IsAuthenticated
from donations.permission import IsOwnerOrAdmin
from django.utils import timezone
from django.shortcuts import get_object_or_404
import uuid
from receipts.models import Billing,BillingStatus,PaymentMethod


class DonationView(GenericAPIView):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=DonationSerializer, responses=DonationSerializer, tags=["Donation"]
    )
    def get(self, request, *args, **kwargs):

        # # ADD HERE (debug)
        # print("USER:", request.user)
        # print("AUTH:", request.user.is_authenticated)
        # print("STAFF:", request.user.is_staff)

        donations = Donation.objects.filter(campaign=kwargs["campaign"])

        serializer = DonationSerializer(
            donations, many=True, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
    request=DonationSerializer, responses=DonationSerializer, tags=["Donation"]
    )
    @extend_schema(
    request=DonationSerializer, responses=DonationSerializer, tags=["Donation"]
    )
    def post(self, request, campaign):
        serializer = self.get_serializer(
            data=request.data, context={"user": request.user}
        )

        if serializer.is_valid():
            # Step 1 - Save donation as PENDING
            donation = serializer.save(
                donor=request.user,
                campaign_id=campaign,
                payment_status='PENDING'   # ← not SUCCESS
            )

            # Step 2 - Create billing as PENDING (no payment yet)
            billing = Billing.objects.create(
                donation=donation,
                recurring_donation=None,
                transaction_id=None,        # ← pidx comes later
                amount=donation.amount,
                currency=donation.currency,
                status=BillingStatus.PENDING,  # ← not SUCCESS
                payment_method=PaymentMethod.KHALTI,
                is_recurring=False,
            )

            # Step 3 - Return billing_id, frontend calls /invoice/{id}/ next
            return Response({
                "message": "Donation created, proceed to payment",
                "donation_id": donation.id,
                "billing_id": billing.id,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class DonationUpdate(GenericAPIView):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=DonationSerializer, responses=DonationSerializer, tags=["Donation"]
    )
    def put(self, request, id):
        donation = Donation.objects.get(id=id)

        serializer = self.get_serializer(
            donation, data=request.data, context={"user": request.user}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=DonationSerializer, responses=DonationSerializer, tags=["Donation"]
    )
    def delete(self, request, id):
        donation = Donation.objects.get(id=id)
        donation.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RecurringDonationView(GenericAPIView):
    queryset = RecurringDonation.objects.all()
    serializer_class = RecurringSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RecurringSerializer,
        responses=RecurringSerializer,
        summary="View recurring donation",
        tags=["Recurring Donation"],
    )
    def get(self, request):
        plan = RecurringDonation.objects.all()
        serializer = RecurringSerializer(plan, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create recurring donation",
        tags=["Recurring Donation"],
        request=RecurringSerializer,
        responses={201: RecurringSerializer},
    )
    def post(self, request):
        serializer = RecurringSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(
                donor=request.user,
                next_run=timezone.now(),  
                is_active=True,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecurringManage(GenericAPIView):
    queryset=RecurringDonation.objects.all()
    serializer_class=RecurringSerializer
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        request=RecurringSerializer,
        responses=RecurringSerializer,
        tags=['Recurring Donation']
    )
    
    def put(self, request, id):
        donation = get_object_or_404(RecurringDonation, id=id)

        serializer = self.get_serializer(
            donation,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @extend_schema(
        request=RecurringSerializer,
        responses=RecurringSerializer,
        tags=['Recurring Donation']
        
    )
    def delete(self, request, id):
        donation = get_object_or_404(RecurringDonation, id=id)
        donation.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
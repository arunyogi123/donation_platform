from campaign.models import Campaign, SubscriptionPlan, CampaignDocument
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import GenericAPIView
from donations.permission import IsOwnerOrAdmin
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from campaign.api.v1.serialziers import (
    CampaignSerializers,
    SubscriptionSerializers,
    CampaignDocumentSerializer,
)


class CampaignView(ListAPIView):
    serializer_class = CampaignSerializers

    def get_queryset(self):
        return Campaign.objects.filter(
            is_approved=True,
            is_active=True
        )

    @extend_schema(
        responses=CampaignSerializers,
        summary="List only approved and active campaigns",
        tags=["Campaign"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=CampaignSerializers,
        responses=CampaignSerializers,
        summary=" Add new campaign",
        tags=["Campaign"],
    )
    def post(self, request):
        data = request.data
        serializer = CampaignSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Successfully added", "data": serializer.data},
                status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=CampaignSerializers,
    responses=CampaignSerializers,
    summary="Delete campaign list ",
    tags=["Campaign"],
)
class CampaignDelete(GenericAPIView):
    queryset = Campaign.objects.all()
    serializer_class = [CampaignSerializers]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    

    def delete(self, request, id):
        plan = Campaign.objects.get(id=id)
        self.check_object_permissions(request, plan)
        plan.delete()
        return Response({"message": "Successfully deleted"}, status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=CampaignSerializers,
    responses=CampaignSerializers,
    summary="Update campaign list ",
    tags=["Campaign"],
)
class CampaigUpdate(GenericAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializers
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def put(self, request, id):
        campaign = get_object_or_404(Campaign, id=id)

        # checks owner OR admin
        self.check_object_permissions(request, campaign)

        serializer = CampaignSerializers(
            campaign,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class SubscriptionView(GenericAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = [SubscriptionSerializers]

    @extend_schema(
        responses=SubscriptionSerializers,
        summary="Get subscription details",
        tags=["Subscription"],
    )
    def get(self, request):
        plan = SubscriptionPlan.objects.all()
        serializer = SubscriptionSerializers(plan, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=SubscriptionSerializers,
        responses=SubscriptionSerializers,
        summary=" Add new subscription",
        tags=["Subscription"],
    )
    def post(self, request):
        data = request.data
        serializer = SubscriptionSerializers(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Successfully added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses=SubscriptionSerializers,
    request=SubscriptionSerializers,
    summary="Update subscription details",
    tags=["Subscription"],
    description="Update Subscription plan instance",
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_subscription(request, id):
    data = request.data
    plan = SubscriptionPlan.objects.get(id=id)
    serializer = SubscriptionSerializers(data=data, instance=plan)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Successfully Updated", "data": serializer.data},
            status.HTTP_200_OK,
        )
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=SubscriptionSerializers,
    responses=SubscriptionSerializers,
    summary="Delete subscription ",
    tags=["Subscription"],
)
class SubscrptionDelete(GenericAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = [SubscriptionSerializers]

    def delete(self, request, id):
        data = SubscriptionPlan.objects.get(id=id)
        data.delete()
        return Response({"message": "Successfully deleted"}, status.HTTP_204_NO_CONTENT)




class DocumentView(GenericAPIView):
    queryset = CampaignDocument.objects.all()
    serializer_class = CampaignDocumentSerializer
    permission_classes = [IsAuthenticated]
    @extend_schema(
        request=CampaignDocumentSerializer,
        responses=CampaignDocumentSerializer,
        tags=['documents']
    )

    def get(self, request, campaign):
        docs = CampaignDocument.objects.filter(campaign_id=campaign)
        serializer = self.get_serializer(
            docs, many=True,
            context={"request": request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        request=CampaignDocumentSerializer,
        responses=CampaignDocumentSerializer,
        tags=['documents']
    )

    def post(self, request, campaign):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(campaign_id=campaign)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentManage(GenericAPIView):
    queryset=CampaignDocument.objects.all()
    serializer_class=CampaignDocumentSerializer
    permission_classes=[IsAuthenticated,IsOwnerOrAdmin]
    
    @extend_schema (
        responses=CampaignDocumentSerializer,
        request=CampaignDocumentSerializer,
        tags=['documents']
    )
    def put(self, request, id):
        doc = CampaignDocument.objects.get(id=id)
        self.check_object_permissions(request, doc)

        serializer = self.get_serializer(
            doc,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        request=CampaignDocumentSerializer,
        responses=CampaignDocumentSerializer,
        tags=['documents']
    )
    def delete(self, request, id):
        doc = CampaignDocument.objects.get(id=id)
        self.check_object_permissions(request, doc)
        
        doc.delete()
        return Response(
    {"message": "Successfully deleted"},
    status=status.HTTP_200_OK
)
from rest_framework import serializers
from campaign.models import Campaign, SubscriptionPlan
from campaign.models import CampaignDocument


class CampaignSerializers(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = "__all__"

   


class SubscriptionSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
        
        



class CampaignDocumentSerializer(serializers.ModelSerializer):

    document = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()
    campaign = serializers.CharField(source="campaign.title", read_only=True)

    class Meta:
        model = CampaignDocument
        fields = "__all__"

    def get_document(self, obj):
        request = self.context.get("request")

        if request and request.user.is_staff:
            return obj.document.url

        return "**"

    def get_document_type(self, obj):
        request = self.context.get("request")

        if request and request.user.is_staff:
            return obj.document_type

        return "**"







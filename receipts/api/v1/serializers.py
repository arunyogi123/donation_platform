from rest_framework import serializers
from receipts.models import Billing


class BillingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Billing
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        campaign = None
        donor_obj = None
        if instance.donation:
            donor_obj = instance.donation.donor
            campaign = instance.donation.campaign
        elif instance.recurring_donation:
            donor_obj = instance.recurring_donation.donor
            campaign = instance.recurring_donation.campaign

        if donor_obj:
            data["donor"] = donor_obj.username
        else:
            data["donor"] = None

        if campaign:
            data["campaign_id"] = campaign.id
            data["campaign_title"] = campaign.title

        is_owner = request and request.user.is_authenticated and (donor_obj == request.user)
        if request and not request.user.is_staff and not is_owner:
            data["transaction_id"] = "****"

        return data
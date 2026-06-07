from rest_framework import serializers
from receipts.models import Billing


class BillingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Billing
        fields = "__all__"

    def to_representation(self, instance):

        data = super().to_representation(instance)

        request = self.context.get("request")

        if request and not request.user.is_staff:
            data["transaction_id"] = "****"

        if instance.donation:
            data["donor"] = instance.donation.donor.username
        elif instance.recurring_donation:
            data["donor"] = instance.recurring_donation.donor.username
        else:
            data["donor"] = None

        return data
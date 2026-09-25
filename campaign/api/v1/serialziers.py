import os
from rest_framework import serializers
from campaign.models import Campaign, SubscriptionPlan, CampaignDocument


ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".webp", ".doc", ".docx"]
MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

DOCUMENT_TYPE_CHOICE_MAP = {
    "medical report": "medical",
    "medical": "medical",
    "id proof": "id",
    "id": "id",
    "ngo certificate": "ngo",
    "ngo": "ngo",
    "other": "other",
}


class CampaignSerializers(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Campaign
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "current_raised", "user"]

    def validate_image(self, value):
        if not value:
            return value
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise serializers.ValidationError(
                f"Unsupported image format '{ext}'. Allowed formats: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}."
            )
        if value.size > MAX_IMAGE_SIZE_BYTES:
            raise serializers.ValidationError(
                f"Image file size ({value.size / (1024 * 1024):.1f}MB) exceeds the 5MB limit."
            )
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        # Ensure image_url reflects uploaded image if present
        if instance.image:
            image_uri = request.build_absolute_uri(instance.image.url) if request else instance.image.url
            data["image"] = image_uri
            data["image_url"] = image_uri
        elif instance.image_url:
            data["image_url"] = instance.image_url

        return data


class SubscriptionSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"


class CampaignDocumentSerializer(serializers.ModelSerializer):
    document = serializers.FileField(required=True)
    document_type = serializers.CharField(required=True)
    campaign = serializers.CharField(source="campaign.title", read_only=True)
    campaign_id = serializers.PrimaryKeyRelatedField(source="campaign", read_only=True)

    class Meta:
        model = CampaignDocument
        fields = "__all__"

    def validate_document(self, value):
        if not value:
            raise serializers.ValidationError("Please select a document file to upload.")
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise serializers.ValidationError(
                f"Unsupported document format '{ext}'. Allowed formats: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}."
            )
        if value.size > MAX_DOCUMENT_SIZE_BYTES:
            raise serializers.ValidationError(
                f"Document file size ({value.size / (1024 * 1024):.1f}MB) exceeds the 10MB limit."
            )
        return value

    def validate_document_type(self, value):
        if not value:
            raise serializers.ValidationError("Document classification is required.")
        val_str = str(value).strip().lower()
        if val_str in DOCUMENT_TYPE_CHOICE_MAP:
            return DOCUMENT_TYPE_CHOICE_MAP[val_str]
        valid_keys = [c[0] for c in CampaignDocument.DOCUMENT_TYPES]
        if val_str in valid_keys:
            return val_str
        raise serializers.ValidationError(
            f"Invalid document classification '{value}'. Must be one of: Medical Report, ID Proof, NGO Certificate, Other."
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        # Authorized if staff or campaign owner
        is_authorized = False
        if request and request.user.is_authenticated:
            campaign_user = getattr(instance.campaign, "user", None)
            if request.user.is_staff or (campaign_user and campaign_user == request.user):
                is_authorized = True

        if is_authorized:
            if instance.document:
                doc_url = request.build_absolute_uri(instance.document.url) if request else instance.document.url
                data["document"] = doc_url
                data["document_name"] = os.path.basename(instance.document.name)
            else:
                data["document"] = None
                data["document_name"] = None
            data["document_type"] = instance.document_type
        else:
            # Sensitive documents remain masked for public / unauthorized users
            data["document"] = "**"
            data["document_name"] = "**"
            data["document_type"] = instance.document_type

        data["document_type_display"] = instance.get_document_type_display()
        return data







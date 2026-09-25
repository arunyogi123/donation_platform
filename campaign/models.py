from django.db import models

# from django.contrib.auth.models import User
from account.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.


class CategoryType(models.TextChoices):
    HEALTH = "HEALTH"
    EDUACTION = "EDUCATION"
    NATURAL_DISASTER = "NATURAL DISASTER"


class Campaign(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20, choices=CategoryType.choices, default=CategoryType.HEALTH
    )
    goal_amount = models.DecimalField(max_digits=20, decimal_places=2)
    current_raised = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    image = models.ImageField(upload_to="campaigns/", blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="campaigns"
    )
    organizer_name = models.CharField(max_length=150, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class CurrencyType(models.TextChoices):
    USD = "USD"
    NPR = "NPR"
    INR = "INR"


class PackageType(models.TextChoices):
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"


class SubscriptionPlan(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.RESTRICT)
    package = models.CharField(
        max_length=10, choices=PackageType.choices, default=PackageType.BASIC
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(
        max_length=5, choices=CurrencyType.choices, default=CurrencyType.USD
    )
    benefits = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.package


class CampaignDocument(models.Model):
    DOCUMENT_TYPES = [
        ("medical", "Medical Report"),
        ("id", "ID Proof"),
        ("ngo", "NGO Certificate"),
        ("other", "Other"),
    ]
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="documents"
    )
    document = models.FileField(upload_to="campaign_docs/")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.campaign.title} - {self.document_type}"

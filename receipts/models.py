from django.db import models
from donations.models import Donation, RecurringDonation


class PaymentMethod(models.TextChoices):
    KHALTI = "KHALTI"
    ESEWA = "ESEWA"
    BANK = "BANK"


class BillingStatus(models.TextChoices):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"


class CurrencyType(models.TextChoices):
    USD = "USD"
    INR = "INR"
    NPR = "NPR"


class Billing(models.Model):

    donation = models.ForeignKey(
        Donation,
        on_delete=models.CASCADE,
        related_name="billings",
        null=True,
        blank=True
    )

    recurring_donation = models.ForeignKey(
        RecurringDonation,
        on_delete=models.CASCADE,
        related_name="billings",
        null=True,
        blank=True
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    currency = models.CharField(
        max_length=5,
        choices=CurrencyType.choices,
        default=CurrencyType.NPR
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.KHALTI
    )

    status = models.CharField(
        max_length=10,
        choices=BillingStatus.choices,
        default=BillingStatus.PENDING
    )

    is_recurring = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.donation:
            return f"Donation {self.donation.id} - {self.status}"
        if self.recurring_donation:
            return f"Recurring {self.recurring_donation.id} - {self.status}"
        return f"{self.id} - {self.status}"
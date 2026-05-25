from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models import F
from dateutil.relativedelta import relativedelta
from campaign.models import Campaign


class CurrencyType(models.TextChoices):
    USD = "USD"
    NPR = "NPR"
    INR = "INR"


class RecurringType(models.TextChoices):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class PaymentType(models.TextChoices):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class Donation(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.RESTRICT)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CurrencyType.choices)
    is_anonymous = models.BooleanField(default=False)

    payment_status = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        old_status = None

        if self.pk:
            old_status = Donation.objects.get(pk=self.pk).payment_status

        super().save(*args, **kwargs)

        # ✅ ONLY UPDATE CAMPAIGN ON FIRST SUCCESS
        if (
            self.payment_status == PaymentType.SUCCESS
            and old_status != PaymentType.SUCCESS
        ):
            # ✅ F() does the math in the DB — no stale reads, no overwrites
            Campaign.objects.filter(pk=self.campaign_id).update(
                current_raised=F('current_raised') + self.amount
            )


    def __str__(self):
        return f"{self.donor} - {self.amount} ({self.payment_status})"


class RecurringDonation(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.RESTRICT)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CurrencyType.choices)

    recurring_timing = models.CharField(
        max_length=10,
        choices=RecurringType.choices
    )

    is_active = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    is_processing = models.BooleanField(default=False)

    next_run = models.DateTimeField(null=True, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)

    last_payment_status = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ SINGLE save() — scheduling only
    def save(self, *args, **kwargs):
        if not self.next_run:
            if self.recurring_timing == RecurringType.WEEKLY:
                self.next_run = timezone.now() + relativedelta(weeks=1)
            elif self.recurring_timing == RecurringType.MONTHLY:
                self.next_run = timezone.now() + relativedelta(months=1)
            elif self.recurring_timing == RecurringType.YEARLY:
                self.next_run = timezone.now() + relativedelta(years=1)

        super().save(*args, **kwargs)

    def calculate_next_run(self):
        base = self.last_run or self.next_run or timezone.now()

        if self.recurring_timing == RecurringType.WEEKLY:
            return base + relativedelta(weeks=1)
        elif self.recurring_timing == RecurringType.MONTHLY:
            return base + relativedelta(months=1)
        elif self.recurring_timing == RecurringType.YEARLY:
            return base + relativedelta(years=1)

    def mark_success(self):
        self.last_payment_status = PaymentType.SUCCESS
        self.last_run = self.next_run
        self.next_run = self.calculate_next_run()
        self.is_processing = False
        self.save()

        # ✅ Atomic campaign update
        Campaign.objects.filter(pk=self.campaign_id).update(
            current_raised=F('current_raised') + self.amount
        )

        RecurringDonationHistory.objects.create(
            recurring_donation=self,
            donor=self.donor,
            campaign=self.campaign,
            amount=self.amount,
            currency=self.currency,
            payment_status=PaymentType.SUCCESS,
            paid_at=timezone.now(),
        )

    def mark_failure(self):
        self.last_payment_status = PaymentType.FAILURE
        self.is_processing = False
        self.save()

    def __str__(self):
        return f"{self.donor} - {self.campaign} - {self.amount} ({self.recurring_timing})"


class RecurringDonationHistory(models.Model):
    recurring_donation = models.ForeignKey(
        RecurringDonation,
        on_delete=models.CASCADE,
        related_name='history'
    )

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.RESTRICT)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CurrencyType.choices)

    payment_status = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.SUCCESS
    )

    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor} - {self.amount} - {self.payment_status}"
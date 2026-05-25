from django.contrib import admin
from .models import Donation, RecurringDonation, RecurringDonationHistory


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ["donor","campaign","amount","payment_status","is_anonymous","created_at"]
    list_filter = ["payment_status"]
    search_fields = ["donor__username", "donor__email"]
  


@admin.register(RecurringDonation)
class RecurringDonationAdmin(admin.ModelAdmin):
    list_display = ["donor","campaign","amount","recurring_timing","is_active","last_payment_status","next_run"]
    list_filter = ["is_active","recurring_timing"]
    search_fields = ["donor__username", "donor__email"]
    


@admin.register(RecurringDonationHistory)
class RecurringDonationHistoryAdmin(admin.ModelAdmin):

    list_display = ["id","donor","campaign","amount","currency","payment_status","paid_at"]
    list_filter = ["paid_at"]
    search_fields = ["donor__username"]

   

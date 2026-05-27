from django.contrib import admin
from .models import Billing

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_donor_email',  
        'get_campaign_title',  
        'payment_method',
        'status',
        'amount',
        'is_recurring',
        'created_at'
    ]
    list_filter = ['status', 'payment_method', 'is_recurring']
    
    def get_donor_email(self, obj):
        if obj.donation:
            return obj.donation.donor.email
        elif obj.recurring_donation:
            return obj.recurring_donation.donor.email  # Access donor through recurring_donation
        return "-"
    get_donor_email.short_description = 'Donor Email'
    
    def get_campaign_title(self, obj):
        if obj.donation:
            return obj.donation.campaign.title
        elif obj.recurring_donation:
            return obj.recurring_donation.campaign.title  # Access campaign through recurring_donation
        return "-"
    get_campaign_title.short_description = 'Campaign'
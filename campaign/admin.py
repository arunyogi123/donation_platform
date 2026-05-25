from django.contrib import admin

# Register your models here.
from .models import Campaign
from .models import SubscriptionPlan,CampaignDocument


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "category", "goal_amount"]
    list_filter = ["is_active"]
    search_fields = ["category", "title"]


@admin.register(SubscriptionPlan)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["package", "amount"]
    search_fields = ["package"]
    
@admin.register(CampaignDocument)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["campaign", "document_type", "uploaded_at"]
    search_fields = ["document_type", "campaign__title"]
    list_filter = ["document_type", "uploaded_at"]





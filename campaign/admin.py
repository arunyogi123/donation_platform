import os
from django.contrib import admin
from django.utils.html import format_html
from .models import Campaign, SubscriptionPlan, CampaignDocument


class CampaignDocumentInline(admin.TabularInline):
    model = CampaignDocument
    extra = 0
    readonly_fields = ["document_preview", "uploaded_at"]
    fields = ["document_type", "document", "document_preview", "uploaded_at"]

    def document_preview(self, obj):
        if not obj.document:
            return "No file attached"
        url = obj.document.url
        name = os.path.basename(obj.document.name)
        ext = os.path.splitext(obj.document.name)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height: 48px; width: 64px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" title="{}" />'
                '</a>',
                url, url, name
            )
        elif ext == ".pdf":
            return format_html(
                '<a href="{}" target="_blank" style="color: #b91c1c; font-weight: 600;">'
                '📄 Open PDF ({})</a>',
                url, name
            )
        return format_html(
            '<a href="{}" target="_blank" style="color: #1d4ed8; font-weight: 600;">'
            '📎 Open File ({})</a>',
            url, name
        )
    document_preview.short_description = "Preview / Link"


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["id", "campaign_image_preview", "title", "submitted_by", "category", "goal_amount", "is_approved", "is_active"]
    list_filter = ["is_approved", "is_active", "category"]
    search_fields = ["category", "title", "organizer_name", "user__email"]
    inlines = [CampaignDocumentInline]
    readonly_fields = ["campaign_image_preview", "created_at", "updated_at"]

    def campaign_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height: 40px; width: 56px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />'
                '</a>',
                obj.image.url, obj.image.url
            )
        if obj.image_url and obj.image_url.startswith("http"):
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height: 40px; width: 56px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />'
                '</a>',
                obj.image_url, obj.image_url
            )
        return "No Image"
    campaign_image_preview.short_description = "Image"

    def submitted_by(self, obj):
        if obj.user:
            return obj.user.email
        return obj.organizer_name or "Anonymous"
    submitted_by.short_description = "Organizer / User"


@admin.register(SubscriptionPlan)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["package", "amount", "campaign"]
    search_fields = ["package", "campaign__title"]
    

@admin.register(CampaignDocument)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "campaign_title", "submitted_by", "document_type", "file_name", "document_preview", "uploaded_at"]
    search_fields = ["document_type", "campaign__title", "campaign__user__email", "campaign__organizer_name"]
    list_filter = ["document_type", "uploaded_at"]
    readonly_fields = ["document_preview", "uploaded_at", "updated_at"]
    fields = ["campaign", "document_type", "document", "document_preview", "uploaded_at", "updated_at"]

    def campaign_title(self, obj):
        return obj.campaign.title
    campaign_title.short_description = "Campaign"

    def submitted_by(self, obj):
        if obj.campaign and obj.campaign.user:
            return obj.campaign.user.email
        return getattr(obj.campaign, "organizer_name", "—")
    submitted_by.short_description = "Submitted By"

    def file_name(self, obj):
        if obj.document:
            return os.path.basename(obj.document.name)
        return "—"
    file_name.short_description = "File Name"

    def document_preview(self, obj):
        if not obj.document:
            return "No file uploaded"
        url = obj.document.url
        name = os.path.basename(obj.document.name)
        ext = os.path.splitext(obj.document.name)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 80px; max-width: 120px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc;" title="{}" />'
                '<br><span style="font-size: 11px; color: #666;">Open image</span></a>',
                url, url, name
            )
        elif ext == ".pdf":
            return format_html(
                '<a href="{}" target="_blank" style="color: #b91c1c; font-weight: 600; text-decoration: underline;">'
                '📄 Open PDF Document</a>'
                '<br><span style="font-size: 11px; color: #666;">{}</span>',
                url, name
            )
        return format_html(
            '<a href="{}" target="_blank" style="color: #1d4ed8; font-weight: 600; text-decoration: underline;">'
            '📎 Open / Download File</a>'
            '<br><span style="font-size: 11px; color: #666;">{}</span>',
            url, name
        )
    document_preview.short_description = "View Document"





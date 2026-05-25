from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User,Profile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "phone","is_verified"]  
    search_fields = ["phone"]  
    
    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user',"full_name","address","created_at"]
    search_fields=['full_name']
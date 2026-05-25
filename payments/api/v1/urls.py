from django.urls import path
from .views import get_payment_url_by_id, callback_khalti

urlpatterns = [
    path('invoice/<int:id>/', get_payment_url_by_id),
    path('callback/', callback_khalti),
]
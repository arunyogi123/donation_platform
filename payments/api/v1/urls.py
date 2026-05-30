from django.urls import path
from .views import initiate_donation, donation_callback, initiate_recurring, recurring_callback

urlpatterns = [
    path('donate/<int:donation_id>/', initiate_donation),
    path('callback/', donation_callback),
    path('recurring/<int:recurring_id>/', initiate_recurring),
    path('recurring/callback/', recurring_callback),
]
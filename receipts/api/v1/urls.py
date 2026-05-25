from django.urls import path
from .views import billing_detail, billing_list

urlpatterns = [
    path('billing/', billing_list),
    path('billing/<int:id>/', billing_detail),
]
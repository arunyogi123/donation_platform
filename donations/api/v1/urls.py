from django.urls import path
from donations.api.v1.views import DonationView,DonationUpdate,RecurringDonationView,RecurringManage

urlpatterns = [
    path("campaign-action/<int:campaign>/", DonationView.as_view(), name="see-data"),
     path("donations/<int:id>/", DonationUpdate.as_view()),
    path("recurring-view",RecurringDonationView.as_view(),name="view=data"),
    path("recurring-manage/<int:id>/", RecurringManage.as_view(), name="update-delete")
    
]
from django.urls import path
from campaign.api.v1.views import SubscriptionView,update_subscription,SubscrptionDelete,CampaignView,CampaignDelete,CampaigUpdate,DocumentView,DocumentManage

urlpatterns = [
    path('campaign-action/', CampaignView.as_view(), name="create-list"),
    path('campaign-delete/<int:id>/', CampaignDelete.as_view(), name="delete-camapaign"),
    path('campaign-update/<int:id>/', CampaigUpdate.as_view(), name="update-camapaign"),
    path('subscription-plan/', SubscriptionView.as_view(), name="subscription-list-create"),
    path('subscription-update/<int:id>/', update_subscription, name="update"),
    path('Subscription-delete/<int:id>', SubscrptionDelete.as_view(), name="delete"),
    path("document-view/<int:campaign>/", DocumentView.as_view()),
    path("documents/<int:id>/", DocumentManage.as_view()),
   
   
]
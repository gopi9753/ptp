from django.urls import path
from payouts.views import PayoutView, BalanceView

urlpatterns = [
    path("api/v1/payouts", PayoutView.as_view()),
    path("api/v1/balance", BalanceView.as_view()),
]
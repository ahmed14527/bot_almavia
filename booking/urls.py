# booking/urls.py

from django.urls import path
from .views import BookingRequestCreateView

urlpatterns = [
    path('booking/', BookingRequestCreateView.as_view(), name='booking-request'),
]

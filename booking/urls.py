# booking/urls.py

from django.urls import path
from .views import BookingRequestCreateView,UploadAccountsView

urlpatterns = [
    path('booking/', BookingRequestCreateView.as_view(), name='booking-request'),
    path("upload-accounts/", UploadAccountsView.as_view(), name="upload-accounts"),

]

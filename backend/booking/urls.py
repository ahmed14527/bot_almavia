from django.urls import path
from .views import (
    api_login,
    api_logout,
    api_me,
    dashboard_stats,
    BookingListCreateView,
    BookingDetailView,
    bulk_delete_bookings,
    start_booking,
    start_batch_bookings,
    cancel_booking,
    resume_booking,
    retry_booking,
    booking_status,
    ExcelPreviewView,
    ExcelConfirmImportView,
    download_excel_template,
    BookingRequestCreateView,
    UploadAccountsView,
)

urlpatterns = [
    # Auth
    path('auth/login/', api_login, name='auth-login'),
    path('auth/logout/', api_logout, name='auth-logout'),
    path('auth/me/', api_me, name='auth-me'),

    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),

    # Bookings / Customers CRUD
    path('bookings/', BookingListCreateView.as_view(), name='bookings-list-create'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='bookings-detail'),
    path('bookings/bulk-delete/', bulk_delete_bookings, name='bookings-bulk-delete'),

    # Workflow Execution Actions
    path('bookings/<int:pk>/start/', start_booking, name='booking-start'),
    path('bookings/start-batch/', start_batch_bookings, name='bookings-start-batch'),
    path('bookings/<int:pk>/cancel/', cancel_booking, name='booking-cancel'),
    path('bookings/<int:pk>/resume/', resume_booking, name='booking-resume'),
    path('bookings/<int:pk>/retry/', retry_booking, name='booking-retry'),
    path('bookings/<int:pk>/status/', booking_status, name='booking-status'),

    # Excel Import Pipeline
    path('excel/preview/', ExcelPreviewView.as_view(), name='excel-preview'),
    path('excel/confirm/', ExcelConfirmImportView.as_view(), name='excel-confirm'),
    path('excel/template/', download_excel_template, name='excel-template'),

    # Backward Compatibility
    path('booking/', BookingRequestCreateView.as_view(), name='booking-request-legacy'),
    path('upload-accounts/', UploadAccountsView.as_view(), name='upload-accounts-legacy'),
]

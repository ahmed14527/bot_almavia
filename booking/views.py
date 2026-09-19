import os
import io
import logging
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Count
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BookingRequest
from .serializers import (
    BookingRequestSerializer,
    BookingStatusSerializer,
    BulkActionSerializer
)
from .tasks import dispatch_booking_job
from .excel_service import validate_and_preview_excel, generate_sample_excel_template

logger = logging.getLogger(__name__)

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
            }
        })
    return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def api_logout(request):
    logout(request)
    return Response({'message': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([AllowAny])
def api_me(request):
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff,
            }
        })
    return Response({
        'authenticated': False,
        'user': None
    })


# ==========================================
# DASHBOARD STATS
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats(request):
    counts = BookingRequest.objects.values('status').annotate(count=Count('id'))
    status_map = {item['status']: item['count'] for item in counts}

    recent_queryset = BookingRequest.objects.all().order_by('-updated_at')[:5]
    recent_serializer = BookingStatusSerializer(recent_queryset, many=True)

    active_queryset = BookingRequest.objects.filter(
        status__in=[BookingRequest.Status.RUNNING, BookingRequest.Status.WAITING_FOR_USER]
    ).order_by('-updated_at')
    active_serializer = BookingStatusSerializer(active_queryset, many=True)

    return Response({
        'total': BookingRequest.objects.count(),
        'pending': status_map.get(BookingRequest.Status.PENDING, 0),
        'running': status_map.get(BookingRequest.Status.RUNNING, 0),
        'waiting_for_user': status_map.get(BookingRequest.Status.WAITING_FOR_USER, 0),
        'success': status_map.get(BookingRequest.Status.SUCCESS, 0),
        'failed': status_map.get(BookingRequest.Status.FAILED, 0),
        'cancelled': status_map.get(BookingRequest.Status.CANCELLED, 0),
        'retrying': status_map.get(BookingRequest.Status.RETRYING, 0),
        'recent_activity': recent_serializer.data,
        'active_jobs': active_serializer.data,
    })


# ==========================================
# BOOKING / CUSTOMER CRUD & LIST
# ==========================================

class BookingListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = BookingRequest.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(passport_number__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(reference_number__icontains=search)
            )

        status_filter = request.query_params.get('status', '').strip().upper()
        if status_filter and status_filter != 'ALL':
            queryset = queryset.filter(status=status_filter)

        nationality = request.query_params.get('nationality', '').strip()
        if nationality:
            queryset = queryset.filter(nationality__iexact=nationality)

        serializer = BookingRequestSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

    def post(self, request):
        serializer = BookingRequestSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save()
            
            auto_start = request.query_params.get('auto_start', '').lower() in ('true', '1')
            if auto_start:
                dispatch_booking_job(booking.id)

            return Response({
                'message': 'Booking customer created successfully.',
                'data': BookingRequestSerializer(booking).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return BookingRequest.objects.get(pk=pk)
        except BookingRequest.DoesNotExist:
            return None

    def get(self, request, pk):
        booking = self.get_object(pk)
        if not booking:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookingRequestSerializer(booking).data)

    def patch(self, request, pk):
        booking = self.get_object(pk)
        if not booking:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookingRequestSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(BookingRequestSerializer(updated).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        booking = self.get_object(pk)
        if not booking:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
        booking.delete()
        return Response({'message': 'Customer deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_delete_bookings(request):
    ids = request.data.get('ids', [])
    if not isinstance(ids, list) or not ids:
        return Response({'error': 'List of IDs is required.'}, status=status.HTTP_400_BAD_REQUEST)

    deleted_count, _ = BookingRequest.objects.filter(id__in=ids).delete()
    return Response({'message': f'Successfully deleted {deleted_count} records.'})


# ==========================================
# WORKFLOW EXECUTION & AUTOMATION ACTIONS
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def start_booking(request, pk):
    try:
        booking = BookingRequest.objects.get(pk=pk)
    except BookingRequest.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status == BookingRequest.Status.RUNNING:
        return Response({'warning': 'Booking automation is already running.'}, status=status.HTTP_400_BAD_REQUEST)

    booking.status = BookingRequest.Status.PENDING
    booking.current_step = "Queued for execution"
    booking.error_message = ""
    booking.save(update_fields=['status', 'current_step', 'error_message', 'updated_at'])

    dispatch_info = dispatch_booking_job(booking.id)
    return Response({
        'message': f'Booking automation started for {booking.email}',
        'booking_id': booking.id,
        'dispatch': dispatch_info
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def start_batch_bookings(request):
    ids = request.data.get('ids', [])
    if not isinstance(ids, list) or not ids:
        return Response({'error': 'A list of booking IDs is required.'}, status=status.HTTP_400_BAD_REQUEST)

    bookings = BookingRequest.objects.filter(id__in=ids)
    started_count = 0
    for b in bookings:
        if b.status != BookingRequest.Status.RUNNING:
            b.status = BookingRequest.Status.PENDING
            b.current_step = "Queued for execution"
            b.error_message = ""
            b.save(update_fields=['status', 'current_step', 'error_message', 'updated_at'])
            dispatch_booking_job(b.id)
            started_count += 1

    return Response({
        'message': f'Successfully initiated workflow for {started_count} bookings.',
        'started_count': started_count
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_booking(request, pk):
    try:
        booking = BookingRequest.objects.get(pk=pk)
    except BookingRequest.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    booking.status = BookingRequest.Status.CANCELLED
    booking.current_step = "Workflow cancelled by user"
    booking.action_required = ""
    booking.save(update_fields=['status', 'current_step', 'action_required', 'updated_at'])
    return Response({'message': 'Booking workflow cancelled.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def resume_booking(request, pk):
    """
    User verification resolution signal for WAITING_FOR_USER state.
    """
    try:
        booking = BookingRequest.objects.get(pk=pk)
    except BookingRequest.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status != BookingRequest.Status.WAITING_FOR_USER:
        return Response({
            'warning': f'Booking is not in WAITING_FOR_USER state (current status: {booking.status})'
        }, status=status.HTTP_400_BAD_REQUEST)

    booking.status = BookingRequest.Status.RUNNING
    booking.current_step = "Resuming after human verification"
    booking.action_required = ""
    booking.save(update_fields=['status', 'current_step', 'action_required', 'updated_at'])

    return Response({'message': 'Resume signal sent. Workflow continuing.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def retry_booking(request, pk):
    try:
        booking = BookingRequest.objects.get(pk=pk)
    except BookingRequest.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    booking.status = BookingRequest.Status.PENDING
    booking.current_step = "Retrying workflow"
    booking.error_message = ""
    booking.save(update_fields=['status', 'current_step', 'error_message', 'updated_at'])

    dispatch_booking_job(booking.id)
    return Response({'message': f'Retrying booking {booking.id}'})


@api_view(['GET'])
@permission_classes([AllowAny])
def booking_status(request, pk):
    try:
        booking = BookingRequest.objects.get(pk=pk)
    except BookingRequest.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(BookingStatusSerializer(booking).data)


# ==========================================
# EXCEL IMPORT & PREVIEW PIPELINE
# ==========================================

class ExcelPreviewView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request):
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({'error': 'An Excel or CSV file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        valid_extensions = ('.xlsx', '.xls', '.csv')
        if not excel_file.name.lower().endswith(valid_extensions):
            return Response({
                'error': f'Invalid file format. Please upload an Excel ({", ".join(valid_extensions)}) file.'
            }, status=status.HTTP_400_BAD_REQUEST)

        preview_result = validate_and_preview_excel(excel_file)
        if not preview_result.get('success'):
            return Response(preview_result, status=status.HTTP_400_BAD_REQUEST)

        return Response(preview_result)


class ExcelConfirmImportView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        accounts = request.data.get('accounts', [])
        if not isinstance(accounts, list) or not accounts:
            return Response({'error': 'No accounts provided for import.'}, status=status.HTTP_400_BAD_REQUEST)

        created_records = []
        errors = []

        for idx, acc in enumerate(accounts):
            try:
                birth_date = acc.get('birth_date')
                if isinstance(birth_date, str):
                    from django.utils.dateparse import parse_date
                    parsed_dob = parse_date(birth_date)
                    if not parsed_dob:
                        try:
                            parsed_dob = datetime.strptime(birth_date, '%d/%m/%Y').date()
                        except Exception:
                            parsed_dob = datetime.strptime(birth_date, '%Y-%m-%d').date()
                    birth_date = parsed_dob

                booking = BookingRequest.objects.create(
                    full_name=acc.get('full_name', '') or acc.get('email', '').split('@')[0],
                    email=acc.get('email'),
                    password=acc.get('password'),
                    passport_number=acc.get('passport_number'),
                    phone_number=str(acc.get('phone_number', '')),
                    nationality=acc.get('nationality'),
                    birth_date=birth_date,
                    status=BookingRequest.Status.PENDING,
                    current_step="Imported from Excel - Pending"
                )
                created_records.append(booking.id)
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

        return Response({
            'message': f'Successfully imported {len(created_records)} customer records.',
            'imported_count': len(created_records),
            'imported_ids': created_records,
            'errors': errors
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def download_excel_template(request):
    content = generate_sample_excel_template()
    response = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="visa_customers_template.xlsx"'
    return response


# ==========================================
# BACKWARD COMPATIBILITY
# ==========================================

class BookingRequestCreateView(BookingListCreateView):
    pass

class UploadAccountsView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)

        preview = validate_and_preview_excel(excel_file)
        if not preview.get('success'):
            return Response(preview, status=status.HTTP_400_BAD_REQUEST)

        # Import valid rows
        valid_accounts = preview.get('valid_rows', [])
        created_ids = []
        for acc in valid_accounts:
            try:
                b = BookingRequest.objects.create(
                    full_name=acc.get('full_name') or acc.get('email').split('@')[0],
                    email=acc['email'],
                    password=acc['password'],
                    passport_number=acc['passport_number'],
                    nationality=acc['nationality'],
                    phone_number=str(acc['phone_number']),
                    birth_date=acc['birth_date'],
                    status=BookingRequest.Status.PENDING,
                )
                created_ids.append(b.id)
                dispatch_booking_job(b.id)
            except Exception as e:
                logger.error(f"Error creating booking from excel: {e}")

        return Response({
            "message": f"Processed Excel file. Imported and started {len(created_ids)} records.",
            "imported_count": len(created_ids),
            "invalid_count": preview.get('invalid_count', 0),
            "invalid_rows": preview.get('invalid_rows', [])
        }, status=status.HTTP_200_OK)

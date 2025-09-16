from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingRequestSerializer
from .models import BookingRequest
from .tasks import run_booking_bot_task, run_booking_bot_parallel
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from celery.result import AsyncResult
from rest_framework.decorators import api_view
from celery.result import GroupResult
from rest_framework.decorators import api_view
from rest_framework.response import Response

class BookingRequestCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if 'nationality' not in request.data:
            return Response({"error": "nationality field is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookingRequestSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save()
            run_booking_bot_task.delay(booking.id)
            return Response({
                "message": "✅ Booking request received successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def check_group_status(request, group_id):
    result = GroupResult.restore(group_id)
    if not result:
        return Response({"error": "Group ID not found."}, status=404)

    return Response({
        "completed": result.completed_count(),
        "total": len(result),
        "statuses": [r.status for r in result.results]
    })

class UploadAccountsView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من نوع الملف
        if not excel_file.name.endswith(('.xls', '.xlsx')):
            return Response({"error": "Invalid file type. Please upload an Excel file."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            return Response({"error": f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = ['email', 'password', 'passport_number', 'phone_number', 'birth_date', 'nationality']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response({"error": f"Missing columns in Excel: {', '.join(missing_columns)}"}, status=400)

        accounts = []
        for _, row in df.iterrows():
            try:
                birth_date = row['birth_date']
                if isinstance(birth_date, str):
                    from django.utils.dateparse import parse_date
                    birth_date = parse_date(birth_date)
                elif hasattr(birth_date, 'to_pydatetime'):
                    birth_date = birth_date.to_pydatetime().date()

                accounts.append({
                    "email": row['email'],
                    "password": row['password'],
                    "passport_number": row['passport_number'],
                    "nationality": row['nationality'],
                    "birth_date": birth_date,
                    "phone_number": str(row['phone_number']),
                    "passport_image_path": row.get('passport_image_path')  
                })
            except Exception as e:
                print(f"❌ Error in row: {row} → {e}")
                continue

        if not accounts:
            return Response({"error": "No valid accounts found in the file."}, status=400)

        from .tasks import run_booking_bot_parallel
        run_booking_bot_parallel.delay(accounts)

        return Response({"message": f"✅ Started processing {len(accounts)} accounts."}, status=200)

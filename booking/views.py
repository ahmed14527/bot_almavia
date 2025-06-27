from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingRequestSerializer
from .models import BookingRequest
from .tasks import run_booking_bot_task  
import pandas as pd
from rest_framework.parsers import MultiPartParser
from celery.result import AsyncResult
from rest_framework.decorators import api_view
from booking.tasks import run_booking_bot_parallel


class BookingRequestCreateView(APIView):
    def post(self, request):
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
def check_task_status(request, task_id):
    result = AsyncResult(task_id)
    if result.state == "PENDING":
        return Response({"state": result.state, "status": "Waiting to be processed"})
    elif result.state == "SUCCESS":
        return Response({"state": result.state, "result": result.result})
    else:
        return Response({"state": result.state})



# booking/views.py

class UploadAccountsView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "File is required"}, status=400)

        df = pd.read_excel(excel_file)
        if "email" not in df.columns or "password" not in df.columns:
            return Response({"error": "Excel must have 'email' and 'password' columns"}, status=400)

        accounts = df[["email", "password"]].values.tolist()

        run_booking_bot_parallel.delay(accounts)  

        return Response({"message": f"{len(accounts)} accounts processing started."})

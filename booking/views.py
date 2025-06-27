from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingRequestSerializer
from .models import BookingRequest
from .tasks import run_booking_bot_task  # استيراد المهمة

class BookingRequestCreateView(APIView):
    def post(self, request):
        serializer = BookingRequestSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save()
            # شغل مهمة celery عشان تبدأ البوت
            run_booking_bot_task.delay(booking.id)  # <=== هنا استدعاء المهمة بشكل غير متزامن
            
            return Response({
                "message": "✅ Booking request received successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

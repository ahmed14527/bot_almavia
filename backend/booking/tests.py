import io
import json
from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from booking.models import BookingRequest
from booking.serializers import BookingRequestSerializer, BookingStatusSerializer
from booking.excel_service import validate_and_preview_excel, generate_sample_excel_template
from booking.bot_runner import run_bot


class BookingModelTests(TestCase):
    def test_create_booking_request(self):
        booking = BookingRequest.objects.create(
            full_name="Ahmed Ali",
            email="ahmed@example.com",
            password="SecretPassword123!",
            passport_number="A12345678",
            phone_number="+201012345678",
            birth_date=date(1990, 5, 15),
            nationality="Egypt",
        )
        self.assertEqual(booking.status, BookingRequest.Status.PENDING)
        self.assertEqual(booking.step_progress, 0)
        self.assertEqual(booking.total_steps, 8)
        self.assertIn("Ahmed Ali", str(booking))
        self.assertIn("A12345678", str(booking))


class SerializerSecurityTests(TestCase):
    def setUp(self):
        self.booking = BookingRequest.objects.create(
            full_name="Fatima Hassan",
            email="fatima@example.com",
            password="VerySecretPassword!",
            passport_number="A99887766",
            phone_number="+201112223334",
            birth_date=date(1993, 8, 20),
            nationality="Egypt",
        )

    def test_password_is_write_only_in_serializer(self):
        serializer = BookingRequestSerializer(self.booking)
        data = serializer.data
        # CRITICAL SECURITY CHECK: Password must NEVER appear in serialized output
        self.assertNotIn("password", data)
        self.assertEqual(data["email"], "fatima@example.com")
        self.assertEqual(data["passport_number"], "A99887766")


class ExcelServiceTests(TestCase):
    def test_generate_and_parse_template(self):
        content = generate_sample_excel_template()
        self.assertTrue(len(content) > 0)

        file_obj = io.BytesIO(content)
        file_obj.name = "template.xlsx"
        result = validate_and_preview_excel(file_obj)

        self.assertTrue(result["success"])
        self.assertEqual(result["total_rows"], 3)
        self.assertEqual(result["valid_count"], 3)
        self.assertEqual(result["invalid_count"], 0)

    def test_validation_catches_invalid_rows(self):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['email', 'password', 'passport_number', 'phone_number', 'birth_date', 'nationality'])
        # Row 2: Valid
        ws.append(['valid@example.com', 'Pass123', 'A12345678', '01012345678', '1990-01-01', 'Egypt'])
        # Row 3: Missing email & invalid passport
        ws.append(['', 'Pass123', '12', '01012345678', '1990-01-01', 'Egypt'])
        # Row 4: Invalid date
        ws.append(['bad.date@example.com', 'Pass123', 'B87654321', '01012345678', 'invalid-date', 'Egypt'])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        buf.name = "test.xlsx"

        result = validate_and_preview_excel(buf)
        self.assertTrue(result["success"])
        self.assertEqual(result["valid_count"], 1)
        self.assertEqual(result["invalid_count"], 2)

        # Check error reporting details
        invalid_rows = result["invalid_rows"]
        row3_errors = next(r for r in invalid_rows if r["row_number"] == 3)
        self.assertTrue(any("email" in err.lower() for err in row3_errors["errors"]))
        self.assertTrue(any("passport" in err.lower() for err in row3_errors["errors"]))

        row4_errors = next(r for r in invalid_rows if r["row_number"] == 4)
        self.assertTrue(any("birth date" in err.lower() for err in row4_errors["errors"]))


class APIEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testadmin", password="TestPassword123!")

        self.booking = BookingRequest.objects.create(
            full_name="Mahmoud Samy",
            email="mahmoud@example.com",
            password="Password456!",
            passport_number="C12349999",
            phone_number="+201555555555",
            birth_date=date(1989, 3, 10),
            nationality="Egypt",
        )

    def test_dashboard_stats(self):
        response = self.client.get("/api/dashboard/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total", response.data)
        self.assertIn("pending", response.data)
        self.assertEqual(response.data["total"], 1)

    def test_bookings_list_and_filter(self):
        response = self.client.get("/api/bookings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        # Search filter
        search_resp = self.client.get("/api/bookings/?search=Mahmoud")
        self.assertEqual(search_resp.data["count"], 1)

        search_none = self.client.get("/api/bookings/?search=NonExistent")
        self.assertEqual(search_none.data["count"], 0)

    def test_booking_actions_lifecycle(self):
        # 1. Start booking
        start_resp = self.client.post(f"/api/bookings/{self.booking.id}/start/")
        self.assertEqual(start_resp.status_code, status.HTTP_200_OK)

        # 2. Status polling
        status_resp = self.client.get(f"/api/bookings/{self.booking.id}/status/")
        self.assertEqual(status_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(status_resp.data["id"], self.booking.id)

        # 3. Simulate WAITING_FOR_USER state and Resume action
        self.booking.status = BookingRequest.Status.WAITING_FOR_USER
        self.booking.action_required = "CAPTCHA required"
        self.booking.save()

        resume_resp = self.client.post(f"/api/bookings/{self.booking.id}/resume/")
        self.assertEqual(resume_resp.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingRequest.Status.RUNNING)
        self.assertEqual(self.booking.action_required, "")

        # 4. Cancel action
        cancel_resp = self.client.post(f"/api/bookings/{self.booking.id}/cancel/")
        self.assertEqual(cancel_resp.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingRequest.Status.CANCELLED)

    def test_excel_confirm_import_api(self):
        accounts_payload = {
            "accounts": [
                {
                    "full_name": "Tamer Hosny",
                    "email": "tamer@example.com",
                    "password": "Pass12345!",
                    "passport_number": "A55443322",
                    "phone_number": "01000000000",
                    "birth_date": "1990-01-15",
                    "nationality": "Egypt"
                }
            ]
        }
        response = self.client.post("/api/excel/confirm/", data=accounts_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["imported_count"], 1)
        self.assertTrue(BookingRequest.objects.filter(passport_number="A55443322").exists())


class BotSimulationWorkflowTests(TestCase):
    def test_bot_simulation_success_path(self):
        booking = BookingRequest.objects.create(
            full_name="Success User",
            email="success.user@example.com",
            password="ValidPassword123!",
            passport_number="A77665544",
            phone_number="01222222222",
            birth_date=date(1991, 7, 7),
            nationality="Egypt",
        )
        success = run_bot(booking_id=booking.id, simulate=True)
        self.assertTrue(success)

        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingRequest.Status.SUCCESS)
        self.assertEqual(booking.step_progress, 8)
        self.assertTrue(len(booking.reference_number) > 0)
        self.assertTrue(len(booking.appointment_date) > 0)

    def test_bot_simulation_failure_path(self):
        booking = BookingRequest.objects.create(
            full_name="Fail User",
            email="fail.user@example.com",
            password="ValidPassword123!",
            passport_number="A00000000",
            phone_number="01222222222",
            birth_date=date(1991, 7, 7),
            nationality="Egypt",
        )
        success = run_bot(booking_id=booking.id, simulate=True)
        self.assertFalse(success)

        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingRequest.Status.FAILED)
        self.assertIn("No appointment slots", booking.error_message)

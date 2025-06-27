from django.db import models

class BookingRequest(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="pending")  # pending / success / failed

    def __str__(self):
        return f"{self.email} - {self.status}"

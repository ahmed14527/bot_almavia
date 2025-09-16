from django.db import models


class BookingRequest(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=255)
    passport_number = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    birth_date = models.DateField()
    nationality = models.CharField(max_length=100)  
    passport_image = models.ImageField(upload_to='passport_images/')  

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="pending")  

    def __str__(self):
        return f"{self.email} - {self.status}"

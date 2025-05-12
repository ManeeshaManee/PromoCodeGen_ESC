from django.db import models

class PromoSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15)
    address = models.TextField()
    promo_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.promo_code}"


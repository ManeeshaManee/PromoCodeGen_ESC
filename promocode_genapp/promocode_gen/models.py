from django.db import models

class PromoSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # ✅ Add unique constraint here
    contact = models.CharField(max_length=15)
    address = models.TextField()
    promo_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

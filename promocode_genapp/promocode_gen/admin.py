
from django.contrib import admin
from .models import PromoSubmission

@admin.register(PromoSubmission)
class PromoSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'promo_code', 'created_at')
    search_fields = ('name', 'email')

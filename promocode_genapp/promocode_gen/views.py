import qrcode
import io
import random
import string
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from .models import PromoSubmission

def generate_qr(data):
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    return buf.getvalue()

def home(request):
    qr_data = request.build_absolute_uri('/scan/')
    qr_image = generate_qr(qr_data)
    return HttpResponse(qr_image, content_type="image/png")

def generate_promo_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def scan_qr(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        address = request.POST['address']
        promo_code = generate_promo_code()

        # Save to DB
        PromoSubmission.objects.create(
            name=name,
            email=email,
            contact=contact,
            address=address,
            promo_code=promo_code
        )

        # Send Email
        send_mail(
            subject="Your 15% Promo Code!",
            message=f"Hello {name},\n\nYour unique promo code is: {promo_code}\nUse it to get 15% off!",
            from_email="promoqr@example.com",
            recipient_list=[email],
        )

        return render(request, 'form.html', {
            'success': True,
            'email': email,
            'promo_code': promo_code
        })

    return render(request, 'form.html')


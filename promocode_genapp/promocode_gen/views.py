import qrcode
import io
import random
import string
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from .models import PromoSubmission
from django.urls import reverse

def generate_qr(data):
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    return buf.getvalue()

import base64

def home(request):
    qr_data = request.build_absolute_uri('/scan/')
    qr_image = generate_qr(qr_data)
    qr_base64 = base64.b64encode(qr_image).decode('utf-8')
    return render(request, 'home.html', {'qr_base64': qr_base64})


def generate_promo_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def scan_qr(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        address = request.POST['address']

        # Check if email already exists
        existing = PromoSubmission.objects.filter(email=email).first()
        if existing:
            promo_code = existing.promo_code
            request.session['email'] = existing.email
            request.session['promo_code'] = promo_code
            request.session['already_exists'] = True
            return redirect('submission_success')

        # Generate new promo code and save
        promo_code = generate_promo_code()
        PromoSubmission.objects.create(
            name=name,
            email=email,
            contact=contact,
            address=address,
            promo_code=promo_code
        )
    


        # Send email
        send_mail(
            "Your Promo Code!",
            f"Hi {name}, your unique promo code for 15% off is: {promo_code}",
            "promoqr@example.com",
            [email],
        )

        

       

        # send_mail(
        #     subject="🎉 Your Exclusive 15% Off Promo Code! - The Collect Room",
        #     message=(
        #         f"Hi {name},\n\n"
        #         "Thank you for being with us! Here is your unique promo code for 15% off:\n\n"
        #         f"👉 {promo_code}\n\n"
        #         "Use this code at checkout to enjoy your discount.\n\n"
        #         "Cheers,\n"
        #         "The Collect Room"
        #     ),
        #     from_email="promoqr@example.com",
        #     recipient_list=[email],
        # )
        


        

        request.session['email'] = email
        request.session['promo_code'] = promo_code
        request.session['already_exists'] = False
        return redirect('submission_success')

    return render(request, 'form.html')


def submission_success(request):
    email = request.session.get('email')
    promo_code = request.session.get('promo_code')
    already_exists = request.session.get('already_exists', False)

    if not email or not promo_code:
        return redirect('scan_qr')  # fallback if accessed directly

    # Clear session data
    request.session.pop('email', None)
    request.session.pop('promo_code', None)
    request.session.pop('already_exists', None)

    return render(request, 'success.html', {
        'email': email,
        'promo_code': promo_code,
        'already_exists': already_exists,
    })

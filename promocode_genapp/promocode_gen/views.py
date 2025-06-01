import qrcode
import io
import random
import string
import base64
import re
from datetime import timedelta
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.template.loader import render_to_string
from .models import PromoSubmission
from django_countries import countries  # Install via pip if not available


def generate_qr(data):
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    return buf.getvalue()
def generate_promo_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)
def is_valid_contact(contact):
    return re.match(r'^\+?\d{7,15}$', contact)  # Supports optional '+' and 7-15 digits
def is_valid_country(country):
    return bool(country.strip())  # Just ensure it's not empty or whitespace

def home(request):
    qr_data = request.build_absolute_uri('/scan/')
    qr_image = generate_qr(qr_data)
    qr_base64 = base64.b64encode(qr_image).decode('utf-8')
    return render(request, 'home.html', {'qr_base64': qr_base64})


def scan_qr(request):
    country_list = [c.name for c in list(countries)]

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        contact = request.POST.get('contact', '').strip()
        address = request.POST.get('address', '').strip()

        errors = {}

        if not is_valid_email(email):
            errors['email'] = "Invalid email format."
        if not is_valid_contact(contact):
            errors['contact'] = "Invalid contact number. Use international format like +1234567890."
        if not is_valid_country(address):
            errors['address'] = "Country field cannot be empty."

        if errors:
            return render(request, 'form.html', {
                'errors': errors,
                'name': name,
                'email': email,
                'contact': contact,
                'address': address,
                'countries': country_list,
            })

        existing = PromoSubmission.objects.filter(email=email).first()
        if existing:
            time_diff = timezone.now() - existing.created_at
            if time_diff < timedelta(days=30):
                request.session['email'] = existing.email
                request.session['promo_code'] = existing.promo_code
                request.session['already_exists'] = True
                return redirect('submission_success')
            else:
                existing.delete()

        promo_code = generate_promo_code()
        PromoSubmission.objects.create(
            name=name,
            email=email,
            contact=contact,
            address=address,
            promo_code=promo_code
        )

        subject = "Your Promo Code!"
        from_email = "digital@thecollectroom.com"
        to_email = [email]

        text_content = f"Hi {name}, your promo code is: {promo_code}"
        html_content = render_to_string('promo_email.html', {
            'name': name,
            'promo_code': promo_code,
        })

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        request.session['email'] = email
        request.session['promo_code'] = promo_code
        request.session['already_exists'] = False
        return redirect('submission_success')

    return render(request, 'form.html', {'countries': country_list})


def submission_success(request):
    email = request.session.get('email')
    promo_code = request.session.get('promo_code')
    already_exists = request.session.get('already_exists', False)

    if not email or not promo_code:
        return redirect('scan_qr')

    request.session.pop('email', None)
    request.session.pop('promo_code', None)
    request.session.pop('already_exists', None)

    return render(request, 'success.html', {
        'email': email,
        'promo_code': promo_code,
        'already_exists': already_exists,
    })
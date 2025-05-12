# import qrcode
# import io
# import random
# import string
# import base64
# from datetime import timedelta

# from django.shortcuts import render, redirect
# from django.core.mail import send_mail
# from django.utils import timezone
# from .models import PromoSubmission

# def generate_qr(data):
#     qr = qrcode.make(data)
#     buf = io.BytesIO()
#     qr.save(buf, format='PNG')
#     return buf.getvalue()

# def generate_promo_code():
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# def home(request):
#     qr_data = request.build_absolute_uri('/promo/scan/')
#     qr_image = generate_qr(qr_data)
#     qr_base64 = base64.b64encode(qr_image).decode('utf-8')
#     return render(request, 'home.html', {'qr_base64': qr_base64})

# def scan_qr(request):
#     if request.method == 'POST':
#         name = request.POST['name']
#         email = request.POST['email']
#         contact = request.POST['contact']
#         address = request.POST['address']

#         existing = PromoSubmission.objects.filter(email=email).first()

#         if existing:
#             time_diff = timezone.now() - existing.created_at
#             if time_diff < timedelta(minutes=5):
#                 # Not expired, reuse promo
#                 request.session['email'] = existing.email
#                 request.session['promo_code'] = existing.promo_code
#                 request.session['already_exists'] = True
#                 return redirect('submission_success')
#             else:
#                 # Expired, delete and allow re-registration
#                 existing.delete()

#         # Create new promo
#         promo_code = generate_promo_code()
#         PromoSubmission.objects.create(
#             name=name,
#             email=email,
#             contact=contact,
#             address=address,
#             promo_code=promo_code
#         )

#         # Send email
#         send_mail(
#             "Your Promo Code!",
#             f"Hi {name}, your unique promo code for 15% off is: {promo_code}",
#             "promoqr@example.com",
#             [email],
#         )

#         request.session['email'] = email
#         request.session['promo_code'] = promo_code
#         request.session['already_exists'] = False
#         return redirect('submission_success')

#     return render(request, 'form.html')

# def submission_success(request):
#     email = request.session.get('email')
#     promo_code = request.session.get('promo_code')
#     already_exists = request.session.get('already_exists', False)

#     if not email or not promo_code:
#         return redirect('scan_qr')

#     # Clear session
#     request.session.pop('email', None)
#     request.session.pop('promo_code', None)
#     request.session.pop('already_exists', None)

#     return render(request, 'success.html', {
#         'email': email,
#         'promo_code': promo_code,
#         'already_exists': already_exists,
#     })
import qrcode
import io
import random
import string
import base64
from datetime import timedelta
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils import timezone
from .models import PromoSubmission
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def generate_qr(data):
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    return buf.getvalue()

def generate_promo_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def home(request):
    qr_data = request.build_absolute_uri('/scan/')
    qr_image = generate_qr(qr_data)
    qr_base64 = base64.b64encode(qr_image).decode('utf-8')
    return render(request, 'home.html', {'qr_base64': qr_base64})

def scan_qr(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        address = request.POST['address']

        existing = PromoSubmission.objects.filter(email=email).first()

        if existing:
            time_diff = timezone.now() - existing.created_at
            if time_diff < timedelta(days=30):
                # Not expired, reuse promo
                request.session['email'] = existing.email
                request.session['promo_code'] = existing.promo_code
                request.session['already_exists'] = True
                return redirect('submission_success')
            else:
                # Expired, delete and allow re-registration
                existing.delete()

        # Create new promo
        promo_code = generate_promo_code()
        PromoSubmission.objects.create(
            name=name,
            email=email,
            contact=contact,
            address=address,
            promo_code=promo_code
        )

        # # Send email
        # send_mail(
        #     "Your Promo Code!",
        #     f"Hi {name}, your unique promo code for 15% off is: {promo_code}",
        #     "promoqr@example.com",
        #     [email],
        # )


        subject = "Your Promo Code!"
        from_email = "promoqr@example.com"
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

    return render(request, 'form.html')

def submission_success(request):
    email = request.session.get('email')
    promo_code = request.session.get('promo_code')
    already_exists = request.session.get('already_exists', False)

    if not email or not promo_code:
        return redirect('scan_qr')

    # Clear session
    request.session.pop('email', None)
    request.session.pop('promo_code', None)
    request.session.pop('already_exists', None)

    return render(request, 'success.html', {
        'email': email,
        'promo_code': promo_code,
        'already_exists': already_exists,
    })

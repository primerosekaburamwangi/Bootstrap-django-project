import logging
import smtplib

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render

from .forms import ContactForm, NewsletterForm

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "index.html")


def contact(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    form = ContactForm(request.POST)
    if not form.is_valid():
        return HttpResponse("Please enter a valid name, email, subject, and message.", status=400)

    return _send_form_email(
        recipient=settings.CONTACT_EMAIL,
        subject=form.cleaned_data["subject"],
        message=(
            f"From: {form.cleaned_data['name']} "
            f"<{form.cleaned_data['email']}>\n\n{form.cleaned_data['message']}"
        ),
        reply_to=[form.cleaned_data["email"]],
    )


def newsletter(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    form = NewsletterForm(request.POST)
    if not form.is_valid():
        return HttpResponse("Please enter a valid email address.", status=400)

    email = form.cleaned_data["email"]
    return _send_form_email(
        recipient=settings.NEWSLETTER_EMAIL,
        subject="Newsletter subscription request",
        message=f"New newsletter subscription request from {email}.",
        reply_to=[email],
    )


def _send_form_email(*, recipient, subject, message, reply_to):
    if not settings.EMAIL_HOST or not recipient or not settings.DEFAULT_FROM_EMAIL:
        return HttpResponse("Email delivery is not configured on this site.", status=503)

    try:
        sent = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            reply_to=reply_to,
        ).send(fail_silently=False)
    except (OSError, smtplib.SMTPException):
        logger.exception("Unable to deliver a website form submission.")
        return HttpResponse("Email delivery failed. Please try again later.", status=503)

    if sent != 1:
        return HttpResponse("Email delivery failed. Please try again later.", status=503)
    return HttpResponse("OK")

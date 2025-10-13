from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_bytes
from django.conf import settings
from .tokens import account_activation_token


def send_activation_email(user):
    uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
    token = account_activation_token.make_token(user)
    activation_link = f"localhost:8000/api/activate/{uid}/{token}" # replace later with frontend url

    mail_subject = _("Activate your account")
    mail_body = _(f"Hello! Please activate your account by clicking the link: {activation_link}")

    send_mail(mail_subject, mail_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


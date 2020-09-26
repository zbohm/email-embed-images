"""Support for Django."""
from typing import Iterable, Optional

from django.conf import settings
from django.core.cache import cache
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives

from email_embed_images.create import create_mail


class EmailMultiRelated(EmailMultiAlternatives):
    """Part Related of e-mail."""
    alternative_subtype = 'related'


class Message:
    """Wrapper for get_connection.send_messages."""

    def __init__(self, msg):
        self.msg = msg

    def message(self):
        """Return mail message."""
        return self.msg


def send_mail(subject: str, message: str, from_email: str, recipient_list: Iterable[str],
              fail_silently: bool = False, auth_user: Optional[str] = None, auth_password: Optional[str] = None,
              connection=None, html_message: Optional[str] = None, attachments: Iterable[str] = None):
    """Send mail with embedded images."""
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = create_mail(
        subject, message, from_email, recipient_list,
        html_message=html_message, attachments=attachments,
        cache=cache, folders_root=[settings.STATIC_ROOT, settings.MEDIA_ROOT]
    )
    return get_connection(fail_silently).send_messages([Message(mail)])

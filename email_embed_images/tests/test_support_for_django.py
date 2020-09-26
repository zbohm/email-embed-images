import os
import unittest
from contextlib import redirect_stdout
from email import message_from_bytes
from io import StringIO

if os.environ.get("DJANGO_SETTINGS_MODULE"):
    from django.test import SimpleTestCase, override_settings

    from email_embed_images.support_for_django import send_mail
else:
    SimpleTestCase = unittest.TestCase


@unittest.skipUnless(os.environ.get("DJANGO_SETTINGS_MODULE"), "requires DJANGO_SETTINGS_MODULE")
class TestSendMail(SimpleTestCase):

    def test_send_mail(self):
        subject = "Test mail"
        from_email = "sender@foo.foo"
        recievers = ["recipient@foo.foo"]
        text_body = "Mail text body."
        html_message = """
            <img src="images/python-logo.png">
            <img src="images/python-logo-generic.svg">
        """
        attachments = ("images/python-logo.png", "images/python-logo-generic.svg")

        with override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'):
            stdout = StringIO()
            with redirect_stdout(stdout):
                send_mail(subject, text_body, from_email, recievers, html_message=html_message, attachments=attachments)

        value = stdout.getvalue()
        content = value.split('\n' + ('-' * 79) + '\n')[0].encode()
        message = message_from_bytes(content)

        self.assertEqual(message["subject"], subject)
        self.assertEqual(message["from"], from_email)
        self.assertEqual(message.get_all("to"), recievers)

        part_alt, attachment_png, attachment_svg = message.get_payload()
        part_text, part_related = part_alt.get_payload()
        part_html, part_png, part_svg = part_related.get_payload()

        self.assertEqual(part_text.get_payload(), 'Mail text body.\n')
        self.assertEqual(part_html.get_payload(),
                         '<html><body><img src="cid:img1"/>\n'
                         '            <img src="cid:img2"/>\n'
                         '        </body></html>\n')
        self.assertEqual(part_png.get('content-type'), 'image/png')
        self.assertEqual(part_png.get('content-id'), 'img1')
        self.assertEqual(part_svg.get('content-type'), 'image/svg+xml')
        self.assertEqual(part_svg.get('content-id'), 'img2')
        self.assertEqual(attachment_png.get('content-type'), 'image/png')
        self.assertEqual(attachment_png.get('content-disposition'), 'attachment; filename="python-logo.png"')
        self.assertEqual(attachment_svg.get('content-type'), 'image/svg+xml')
        self.assertEqual(attachment_svg.get('content-disposition'), 'attachment; filename="python-logo-generic.svg"')

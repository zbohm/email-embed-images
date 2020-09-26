from pyfakefs.fake_filesystem_unittest import TestCase as FakeFsTestCase

from email_embed_images.create import create_mail


class TestCreateMail(FakeFsTestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def test_create_mail(self):
        with open("picture.png", "w") as handle:
            handle.write("PNG")
        with open("icon.gif", "w") as handle:
            handle.write("GIF")
        with open("example.pdf", "w") as handle:
            handle.write("PDF")
        with open("chengelog.txt", "w") as handle:
            handle.write("TXT")

        subject = "Test mail"
        from_email = "sender@foo.foo"
        recievers = ["recipient@foo.foo"]
        cc = ["cc1@foo.foo", "cc2@foo.foo"]
        bcc = ["bcc1@foo.foo"]
        reply_to = ["reply-to@foo.foo"]
        headers = [("message-id", "42")]
        text_body = "Mail text body."
        html_message = """
            <img src="picture.png">
            <img src="icon.gif">
        """
        attachments = ("example.pdf", "chengelog.txt")

        mail = create_mail(subject, text_body, from_email, recievers, cc, bcc, reply_to, html_message, attachments,
                           headers)

        self.assertEqual(mail.get("subject"), "Test mail")
        self.assertEqual(mail.get("from"), "sender@foo.foo")
        self.assertEqual(mail.get("to"), "recipient@foo.foo")
        self.assertEqual(mail.get("cc"), "cc1@foo.foo, cc2@foo.foo")
        self.assertEqual(mail.get("bcc"), "bcc1@foo.foo")
        self.assertEqual(mail.get("reply-to"), "reply-to@foo.foo")

        part_alt, attachment_pdf, attachment_log = mail.get_payload()
        part_text, part_related = part_alt.get_payload()
        part_html, part_png, part_gif = part_related.get_payload()

        self.assertEqual(part_text.get_payload(), 'Mail text body.\n')
        self.assertEqual(part_html.get_payload(),
                         '<html><body><img src="cid:img1"/>\n'
                         '            <img src="cid:img2"/>\n'
                         '        </body></html>\n')
        self.assertEqual(part_png.get('content-type'), 'image/png')
        self.assertEqual(part_png.get('content-id'), 'img1')
        self.assertEqual(part_gif.get('content-type'), 'image/gif')
        self.assertEqual(part_gif.get('content-id'), 'img2')
        self.assertEqual(attachment_pdf.get('content-type'), 'application/pdf')
        self.assertEqual(attachment_pdf.get('content-disposition'), 'attachment; filename="example.pdf"')
        self.assertEqual(attachment_log.get('content-type'), 'text/plain')
        self.assertEqual(attachment_log.get('content-disposition'), 'attachment; filename="chengelog.txt"')

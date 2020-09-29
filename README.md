[![Build Status](https://travis-ci.org/zbohm/email-embed-images.svg?branch=master)](https://travis-ci.org/zbohm/email-embed-images)
[![Coverage](https://codecov.io/gh/zbohm/email-embed-images/branch/master/graph/badge.svg)](https://codecov.io/gh/zbohm/email-embed-images)

# Email embed images

Create e-mail with embedded images, the path of which it takes from the HTML part of the email.
The function finds and replaces expressions `<img src="..." ...>` and `<input type="image" src="..." ...>`.

## Usage

Following example shows how to create e-mail with embedded images readed from the local folder
or images downloaded from the internet.

Images in local folder are placed relatively to the root defined in parameter `folders_root`.
Default is `["."]`, therefore pictures are taken from the subfolder `images` in the project.

The function `create_mail` uses simple file cache that stores files downloaded from the internet
to the temporary folder `email-embed-images` (`/tmp/email-embed-images`). Therefore,
the files are downloaded only once. You can define your own cache in parameter `cache`.


```python
import smtplib
from email.headerregistry import Address

from email_embed_images.create import create_mail

# Prepare TEXT part of mail. This part is mandatory.
body_text = """
Local logo: python-logo.png
Web logo: python-logo-generic.svg
"""

# Prepare HTML part of mail. This part is optional.
# Example embed local file `python-logo.png` from subfolder `images`
# and logo `python-logo-generic.svg` from url on `www.python.org`.
# Download from https://www.python.org/static/img/python-logo.png
# and https://www.python.org/static/community_logos/python-logo-generic.svg.
body_html = """
<body>
    <p>
        Local logo:
        <img src="images/python-logo.png" width="290" height="82" alt="logo local">
    </p>
    <p>
        Web logo:
        <img src="https://www.python.org/static/community_logos/python-logo-generic.svg"
            width="518" height="153" alt="logo from python.org">
    </p>
</body>
"""

# Prepare attachments of mail. This part is optional.
# Example embed local file `python-logo-generic.svg` from subfolder `images`
# and logo `python-powered-h-50x65.png` from url on `www.python.org`.
attachments = (
    "images/python-logo-generic.svg",
    "https://www.python.org/static/community_logos/python-powered-h-50x65.png",
)

# You can also type simple: `from_email = "Stanley Sender <sender@example.com>"`
from_email = Address("Stanley Sender", "sender", "example.com")
recipient_list = [
    Address("Robert Recipient", "recipient", "example.com"),
]
subject = "The test of embedded images and attachemnts"

# Create e-mail instance.
msg = create_mail(subject, body_text, from_email, recipient_list,
                  html_message=body_html, attachments=attachments)

# You can save instance into file in format EML.
with open("test-mail.eml", "wb") as handle:
    handle.write(msg.as_bytes())

# You can send it if you have a working mail server.
with smtplib.SMTP('localhost') as server:
    server.sendmail(from_email, recipient_list, msg.as_string())
```

## Usage in Django

There is support for [Django](https://www.djangoproject.com/).
Function `send_mail` is compatible with `send_mail` in `django.core.mail`.
The function uses Django `cache` and as a folder roots `STATIC_ROOT` and  `MEDIA_ROOT`.

```python
from email_embed_images.support_for_django import send_mail

send_mail(subject, body_text, from_email, recipient_list, html_message=body_html)
```

### Testing

Project has a test suite, powered by tox. To run it, type this:

```
$ virtualenv --python=/usr/bin/python3 env
$ source env/bin/activate
(env) $ pip install -e git+https://github.com/zbohm/email-embed-images.git#egg=email-embed-images[quality,test]
(env) $ cd env/src/email-embed-images/
(env) $ tox --skip-missing-interpreters
$ deactivate
```

The project is licensed under [BSD 3-Clause License](LICENSE).

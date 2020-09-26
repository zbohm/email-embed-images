"""Email creator."""
from email.message import EmailMessage
from typing import Iterable, List, Tuple, Union

from .cache import TemporaryFolderCache
from .collect import CollectImages

COMMASPACE = ', '


def create_mail(
        subject: str,
        text_body: str,
        from_email: str,
        recievers: Iterable[str],
        cc: Iterable[str] = None,
        bcc: Iterable[str] = None,
        reply_to: Iterable[str] = None,
        html_message: str = None,
        attachments=None,
        headers: Iterable[Tuple[str, str]] = None,
        cache=None,  # An instance of class with functions cache.get(key) and cache.set(key, value).
        folders_root: List[str] = None,
        requests_timeout: Union[int, Tuple[int, int]] = None,
        encoding: str = "UTF-8"):
    """Create email object."""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = COMMASPACE.join(recievers)
    if cc is not None:
        msg['Cc'] = COMMASPACE.join(cc)
    if bcc is not None:
        msg['Bcc'] = COMMASPACE.join(bcc)
    if reply_to is not None:
        msg['Reply-To'] = COMMASPACE.join(reply_to)
    if headers is not None:
        for name, value in headers:
            msg[name] = value

    files_cache = TemporaryFolderCache() if cache is None else cache
    collector = CollectImages(files_cache, folders_root, requests_timeout)

    msg.set_content(text_body, charset=encoding)
    if html_message:
        html_body, images = collector.collect_images(html_message, encoding)
        msg.add_alternative(html_body, subtype='html', charset=encoding)
        if images:
            alt = msg.get_payload()[1]
            for item in images:
                maintype, subtype, cid, content = item
                alt.add_related(content, maintype, subtype, cid=cid)

    if attachments:
        for item in collector.collect_attachments(attachments):
            maintype, subtype, filename, content = item
            msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)
    return msg

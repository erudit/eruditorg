from base64 import urlsafe_b64encode
from binascii import unhexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from datetime import datetime
from django.conf import settings
from urllib.parse import quote


def generate_casa_token(
    subscription_id=1,
    token_separator=":",
    invalid_nonce=False,
    invalid_message=False,
    invalid_signature=False,
    payload_separator=":",
    time_delta=0,
    ip_subnet="127.0.0.0/24",
):
    nonce = get_random_bytes(12)
    payload = "{timestamp}{separator}{subscription_id}{separator}{ip_subnet}".format(
        **{
            "timestamp": int(datetime.now().timestamp() * 1000000) - time_delta,
            "subscription_id": subscription_id,
            "ip_subnet": quote(ip_subnet, safe=""),
            "separator": payload_separator,
        }
    )
    key = getattr(settings, "GOOGLE_CASA_KEY", None)
    cipher = AES.new(unhexlify(key), AES.MODE_GCM, nonce=nonce)
    message, signature = cipher.encrypt_and_digest(payload.encode())
    if invalid_nonce:
        nonce = get_random_bytes(12)
    if invalid_message:
        message = get_random_bytes(12)
    if invalid_signature:
        signature = get_random_bytes(12)
    return (
        urlsafe_b64encode(nonce) + token_separator.encode() + urlsafe_b64encode(message + signature)
    )

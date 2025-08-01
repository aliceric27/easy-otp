from base64 import (
    b32encode,
    b64decode,
)
from collections.abc import Generator
from typing import (
    List,
    Union,
)
from urllib.parse import (
    parse_qs,
    quote,
    urlencode,
    urlparse,
)


from src.utils.otpauth_migration.enums import (
    Algorithm,
    DigitCount,
    OtpType,
)
from src.utils.otpauth_migration.protobuf.otpauth_migration_pb2 import Payload


SCHEME = 'otpauth-migration'
HOSTNAME = 'offline'
PAYLOAD_MARK = 'data'
EXAMPLE_PAYLOAD = 'CjEKCkhlbGxvId6tvu8SGEV4YW1wbGU6YWxpY2VAZ29vZ2xlLmNvbRoHRXhhbXBsZTAC'
EXAMPLE_MIGRATION = f'{SCHEME}://{HOSTNAME}?{PAYLOAD_MARK}={EXAMPLE_PAYLOAD}'


def parse_migration_uri(uri: str) -> List[str]:
    """
    將 Google Authenticator 的 otpauth-migration:// URI
    轉成多條標準 otpauth://… 連結。
    """
    url = urlparse(uri)
    qs = parse_qs(url.query)

    # 確認這是合規的 migration 連結
    if url.scheme != "otpauth-migration" or PAYLOAD_MARK not in qs:
        raise ValueError("Invalid otpauth-migration URI")

    links: List[str] = []
    for payload_bytes in decoded_data(qs[PAYLOAD_MARK]):
        payload = Payload()
        payload.ParseFromString(payload_bytes)
        for otp in payload.otp_parameters:
            links.append(get_otpauth_url(otp))
    return links


def decoded_data(data: List[str]) -> Generator:
    for data_item in data:
        yield b64decode(data_item)


def decode_secret(secret: bytes) -> str:
    return str(b32encode(secret), 'utf-8').replace('=', '')


def get_url_params(otp: Payload.OtpParameters) -> str:
    params: dict[str, Union[str, int]] = {}

    if otp.algorithm:
        params.update(algorithm=Algorithm.get(otp.algorithm, ''))
    if otp.digits:
        params.update(digits=DigitCount.get(otp.digits, ''))
    if otp.issuer:
        params.update(issuer=otp.issuer)
    if otp.secret:
        otp_secret = decode_secret(otp.secret)
        params.update(secret=otp_secret)

    return urlencode(params)


def get_otpauth_url(otp: Payload.OtpParameters) -> str:
    otp_type = OtpType.get(otp.type, '')
    otp_name = quote(otp.name)
    otp_params = get_url_params(otp)

    return f'otpauth://{otp_type}/{otp_name}?{otp_params}'

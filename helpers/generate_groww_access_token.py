import pyotp
from dotenv import load_dotenv
from growwapi import GrowwAPI

load_dotenv()

def generate_groww_access_token(totp_token: str, totp_secret: str) -> str:
  totp_gen = pyotp.TOTP(totp_secret)
  totp = totp_gen.now()
  access_token = GrowwAPI.get_access_token(api_key = totp_token, totp = totp)
  return access_token

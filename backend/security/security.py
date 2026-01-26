# security.py
import os
import time
import requests
from typing import Dict, Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv

from observability import observe

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("API_AUDIENCE")
ALGORITHMS = [os.getenv("ALGORITHMS", "RS256")]

if not AUTH0_DOMAIN or not API_AUDIENCE:
    raise RuntimeError("AUTH0_DOMAIN and API_AUDIENCE must be set")

JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

_jwks_cache: Dict[str, Any] = {"keys": [], "fetched_at": 0}
JWKS_CACHE_SECONDS = 3600


@observe()
def _fetch_jwks(force: bool = False) -> Dict[str, Any]:
    now = time.time()
    if force or not _jwks_cache["keys"] or (now - _jwks_cache["fetched_at"] > JWKS_CACHE_SECONDS):
        resp = requests.get(JWKS_URL, timeout=5)
        resp.raise_for_status()
        _jwks_cache["keys"] = resp.json().get("keys", [])
        _jwks_cache["fetched_at"] = now
    return _jwks_cache


def _get_rsa_key(unverified_header: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    jwks = _fetch_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == unverified_header.get("kid"):
            return {
                "kty": key.get("kty"),
                "kid": key.get("kid"),
                "use": key.get("use"),
                "n": key.get("n"),
                "e": key.get("e"),
            }
    return None


@observe()
def get_user_email_from_auth0(token: str) -> Optional[str]:
    try:
        response = requests.get(
            f"https://{AUTH0_DOMAIN}/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        response.raise_for_status()
        return response.json().get("email")
    except Exception:
        return None


@observe()
def validate_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = _get_rsa_key(unverified_header)

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        payload["_raw_token"] = token
        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

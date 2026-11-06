"""Authentication helpers for NutriOrder AI's Flask API."""

from __future__ import annotations

import hashlib
import os
import re
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib.parse import quote

from flask import current_app, session
from werkzeug.security import check_password_hash, generate_password_hash

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_email(value: object) -> str:
    return value.strip().lower() if isinstance(value, str) else ""


def valid_email(email: str) -> bool:
    return len(email) <= 254 and bool(EMAIL_RE.match(email))


def password_error(password: object) -> str | None:
    if not isinstance(password, str) or len(password) < 10:
        return "Use a password with at least 10 characters."
    if len(password) > 128:
        return "Password must be 128 characters or fewer."
    if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
        return "Include at least one letter and one number in your password."
    return None


def validate_customer_registration(data: dict) -> tuple[str | None, dict | None]:
    full_name = data.get("full_name", "")
    email = normalize_email(data.get("email"))
    phone = data.get("phone", "")
    password = data.get("password", "")

    if not isinstance(full_name, str) or not full_name.strip() or len(full_name.strip()) > 100:
        return "Enter your name (up to 100 characters).", None
    if not valid_email(email):
        return "Enter a valid email address.", None
    if not isinstance(phone, str) or not re.fullmatch(r"[+0-9()\-\s]{7,20}", phone.strip()):
        return "Enter a valid phone number.", None
    issue = password_error(password)
    if issue:
        return issue, None
    return None, {
        "full_name": full_name.strip(),
        "email": email,
        "phone": phone.strip(),
        "password": password,
    }


def verify_or_upgrade_password(user, password: str, connection) -> bool:
    password_hash = user["password_hash"]
    if password_hash:
        try:
            return check_password_hash(password_hash, password)
        except (ValueError, TypeError):
            return False

    # One-time compatibility for the original demo database. Successful legacy
    # logins are immediately converted to Werkzeug's salted password hash.
    legacy_password = user["password"]
    if legacy_password and secrets.compare_digest(str(legacy_password), password):
        connection.execute(
            "UPDATE users SET password_hash = ?, password = '' WHERE id = ?",
            (generate_password_hash(password), user["id"]),
        )
        connection.commit()
        return True
    return False


def create_session(user, remember: bool = False) -> dict:
    session.clear()
    session["user_id"] = int(user["id"])
    role = "owner" if user["role"] == "bakery" else user["role"]
    session["role"] = role
    session.permanent = remember
    return {
        "id": int(user["id"]),
        "username": user["username"],
        "full_name": user["full_name"] or user["username"],
        "email": user["email"],
        "role": role,
    }


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _send_reset_email(email: str, token: str) -> None:
    host = os.getenv("MAIL_SERVER")
    sender = os.getenv("MAIL_FROM")
    if not host or not sender:
        raise RuntimeError("Password recovery email is not configured.")

    frontend_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:8000/frontend").rstrip("/")
    reset_url = f"{frontend_url}/reset-password.html?token={quote(token)}"
    message = EmailMessage()
    message["Subject"] = "Reset your NutriOrder AI password"
    message["From"] = sender
    message["To"] = email
    message.set_content(
        "We received a request to reset the password for your NutriOrder AI account.\n\n"
        f"Use this one-time link within 30 minutes: {reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    port = int(os.getenv("MAIL_PORT", "587"))
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    with smtplib.SMTP(host, port, timeout=15) as smtp:
        smtp.starttls()
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)


def issue_password_reset(email: str, connection) -> None:
    """Store only a hashed, expiring token; send it only through configured SMTP."""
    user = connection.execute(
        "SELECT id, email FROM users WHERE email = ? COLLATE NOCASE AND is_active = 1",
        (email,),
    ).fetchone()
    if not user:
        return

    raw_token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    connection.execute(
        "UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE user_id = ? AND used_at IS NULL",
        (user["id"],),
    )
    connection.execute(
        "INSERT INTO password_resets (user_id, token_hash, expires_at) VALUES (?, ?, ?)",
        (user["id"], _hash_token(raw_token), expires_at),
    )
    connection.commit()
    try:
        _send_reset_email(user["email"], raw_token)
    except Exception:
        current_app.logger.warning("Password reset email delivery is not available.")
        raise


def consume_password_reset(token: str, new_password: str, connection) -> bool:
    reset = connection.execute(
        """SELECT id, user_id, expires_at FROM password_resets
           WHERE token_hash = ? AND used_at IS NULL""",
        (_hash_token(token),),
    ).fetchone()
    if not reset:
        return False
    try:
        expiry = datetime.fromisoformat(reset["expires_at"])
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return False
    if expiry <= datetime.now(timezone.utc):
        return False

    connection.execute(
        "UPDATE users SET password_hash = ?, password = '' WHERE id = ?",
        (generate_password_hash(new_password), reset["user_id"]),
    )
    connection.execute(
        "UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE id = ?",
        (reset["id"],),
    )
    connection.commit()
    return True

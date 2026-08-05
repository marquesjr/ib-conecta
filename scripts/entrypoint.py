#!/usr/bin/env python
import os
import subprocess
import sys


def run(cmd: list[str]) -> None:
    subprocess.check_call(cmd)


def ensure_superuser() -> None:
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    if not username or not password:
        return

    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
    script = f"""
from django.contrib.auth import get_user_model
User = get_user_model()
username = {username!r}
email = {email!r}
password = {password!r}
user, created = User.objects.get_or_create(username=username, defaults={{'email': email}})
if created or not user.check_password(password):
    user.email = email or user.email
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
"""
    run([sys.executable, "manage.py", "shell", "-c", script])


def main() -> None:
    run([sys.executable, "manage.py", "migrate", "--noinput"])
    ensure_superuser()
    os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("entrypoint requires a command")
    main()

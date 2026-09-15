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


def bootstrap_cms() -> None:
    script = """
from apps.public.bootstrap import bootstrap_cms
bootstrap_cms()
"""
    run([sys.executable, "manage.py", "shell", "-c", script])


def discard_due_sensitive_data() -> None:
    run([sys.executable, "manage.py", "discard_retreat_sensitive_data"])


def seed_demo_if_enabled() -> None:
    flag = os.environ.get("DJANGO_SEED_DEMO", "").lower()
    if flag not in {"1", "true", "yes", "on"}:
        return
    debug = os.environ.get("DJANGO_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    if not debug:
        return
    run([sys.executable, "manage.py", "seed_demo"])


def collectstatic_if_enabled() -> None:
    flag = os.environ.get("DJANGO_COLLECTSTATIC", "").lower()
    if flag not in {"1", "true", "yes", "on"}:
        return
    run([sys.executable, "manage.py", "collectstatic", "--noinput"])


def main() -> None:
    run([sys.executable, "manage.py", "migrate", "--noinput"])
    collectstatic_if_enabled()
    ensure_superuser()
    bootstrap_cms()
    discard_due_sensitive_data()
    seed_demo_if_enabled()
    os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("entrypoint requires a command")
    main()

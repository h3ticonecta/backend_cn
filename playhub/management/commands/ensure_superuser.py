import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Cria o superusuário a partir de DJANGO_SUPERUSER_* (Railway) "
        "ou redefine a senha se DJANGO_SUPERUSER_RESET_PASSWORD=true."
    )

    def handle(self, *args, **options):
        username = (os.environ.get("DJANGO_SUPERUSER_USERNAME") or "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "admin@playhub.local").strip()

        if not username or not password:
            self.stdout.write(
                "Nenhum superusuário criado: defina DJANGO_SUPERUSER_USERNAME e "
                "DJANGO_SUPERUSER_PASSWORD no ambiente."
            )
            return

        User = get_user_model()
        reset = os.environ.get("DJANGO_SUPERUSER_RESET_PASSWORD", "").lower() in (
            "1",
            "true",
            "yes",
        )

        user = User.objects.filter(username=username).first()
        if user is None:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f"Superusuário '{username}' criado."))
            return

        if reset:
            user.set_password(password)
            user.email = email or user.email
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["password", "email", "is_staff", "is_superuser"])
            self.stdout.write(
                self.style.WARNING(f"Senha do usuário '{username}' atualizada (RESET).")
            )
            return

        if user.is_superuser and user.is_staff:
            self.stdout.write(f"Superusuário '{username}' já existe (senha não alterada).")
            return

        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Conta '{username}' promovida a superusuário."))

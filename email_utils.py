import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
BASE_URL = os.getenv("VERIFICATION_BASE_URL", "http://localhost:8000")


def send_pin_email(to: str, nombre: str, pin: str):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": "Tu PIN de verificación - MediApp",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Hola {nombre}, ya casi terminás</h2>
            <p>Ingresá este PIN en la aplicación para confirmar tu cuenta. Expira en <strong>10 minutos</strong>.</p>
            <div style="font-size: 40px; font-weight: bold; letter-spacing: 12px;
                        text-align: center; padding: 24px; background: #f3f4f6;
                        border-radius: 8px; margin: 16px 0; color: #1d4ed8;">
                {pin}
            </div>
            <p style="color: #6b7280; font-size: 14px;">
                Si no creaste una cuenta en MediApp podés ignorar este mensaje.
            </p>
        </div>
        """
    })


def send_verification_email(to: str, nombre: str, token: str, user_type: str):
    verify_url = f"{BASE_URL}/auth/{user_type}/verificar?token={token}"

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": "Verificá tu cuenta en MediApp",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Hola {nombre}, bienvenido/a a MediApp</h2>
            <p>Para activar tu cuenta hacé clic en el botón de abajo. El enlace expira en 24 horas.</p>
            <a href="{verify_url}"
               style="display: inline-block; padding: 12px 24px; background-color: #2563eb;
                      color: white; text-decoration: none; border-radius: 6px; margin: 16px 0;">
                Verificar cuenta
            </a>
            <p style="color: #6b7280; font-size: 14px;">
                Si no creaste una cuenta en MediApp podés ignorar este mensaje.
            </p>
        </div>
        """
    })

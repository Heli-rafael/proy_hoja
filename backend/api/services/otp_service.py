import secrets
from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone

from ..models import OTP

OTP_EXPIRATION_MINUTES = 5

# POR DEFECTO LOGIN
def generate_otp(email, user=None, purpose="login"):

    # Validacion
    valid_purposes = {
        "login",
        "register",
        "reset_password",
    }

    if purpose not in valid_purposes:
        raise ValueError(
            f"Propósito de OTP no válido: {purpose}"
        )

    # Invalidar OTPs anteriores
    OTP.objects.filter(
        email=email,
        purpose=purpose,
        is_used=False,
    ).update(
        is_used=True
    )

    code = f"{secrets.randbelow(1_000_000):06d}"

    otp = OTP.objects.create(
        user=user,
        email=email,
        code=code,
        purpose=purpose,
        expires_at=(
            timezone.now()
            + timedelta(minutes=OTP_EXPIRATION_MINUTES)
        ),
    )

    return otp


# USAR FORMATOS

from api.services.otp_formato.register import send_register_otp_email
from api.services.otp_formato.recovery import send_recovery_otp_email
from api.services.otp_formato.security import send_security_otp_email


OTP_EMAIL_HANDLERS = {
    "register": send_register_otp_email,
    "reset_password": send_recovery_otp_email,
    "login": send_security_otp_email,
}




# BORRAR
from django.core.mail import EmailMultiAlternatives

def send_otp_email(otp):
    subject = "Tu código de verificación"

    text_content = f"""
Hola,

Hemos recibido una solicitud de verificación.

Tu código de verificación es: {otp.code}

Este código expira en {OTP_EXPIRATION_MINUTES} minutos.
Por seguridad, no compartas este código con nadie.

Si no realizaste esta solicitud, puedes ignorar este correo.

Saludos,
El equipo de AgroVisionAI
""".strip()

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>

<body style="
    margin: 0;
    padding: 0;
    background-color: #f4f6f8;
    font-family: Arial, Helvetica, sans-serif;
    color: #1f2937;
">

    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color: #f4f6f8; padding: 40px 20px;">

        <tr>
            <td align="center">

                <table width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="
                           max-width: 520px;
                           background-color: #ffffff;
                           border-radius: 12px;
                           overflow: hidden;
                           box-shadow: 0 4px 15px rgba(0,0,0,0.06);
                       ">

                    <!-- Header -->
                    <tr>
                        <td style="
                            background-color: #111827;
                            padding: 28px 30px;
                            text-align: center;
                        ">
                            <div style="
                                color: #ffffff;
                                font-size: 22px;
                                font-weight: bold;
                            ">
                                Verificación de cuenta
                            </div>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 36px 30px;">

                            <h1 style="
                                margin: 0 0 16px 0;
                                font-size: 24px;
                                color: #111827;
                            ">
                                Tu código de verificación
                            </h1>

                            <p style="
                                margin: 0 0 24px 0;
                                font-size: 15px;
                                line-height: 1.6;
                                color: #4b5563;
                            ">
                                Hemos recibido una solicitud de verificación.
                                Utiliza el siguiente código para continuar:
                            </p>

                            <!-- OTP -->
                            <div style="
                                margin: 30px 0;
                                padding: 20px;
                                background-color: #f3f4f6;
                                border: 1px solid #e5e7eb;
                                border-radius: 10px;
                                text-align: center;
                            ">
                                <div style="
                                    font-size: 32px;
                                    font-weight: bold;
                                    letter-spacing: 8px;
                                    color: #111827;
                                ">
                                    {otp.code}
                                </div>
                            </div>

                            <!-- Expiration -->
                            <p style="
                                margin: 0 0 20px 0;
                                text-align: center;
                                font-size: 14px;
                                color: #6b7280;
                            ">
                                Este código expira en
                                <strong style="color: #111827;">
                                    {OTP_EXPIRATION_MINUTES} minutos
                                </strong>.
                            </p>

                            <!-- Security notice -->
                            <div style="
                                margin-top: 28px;
                                padding: 16px;
                                background-color: #fff7ed;
                                border-left: 4px solid #f97316;
                                border-radius: 6px;
                            ">
                                <p style="
                                    margin: 0;
                                    font-size: 13px;
                                    line-height: 1.5;
                                    color: #9a3412;
                                ">
                                    Por seguridad, nunca compartas este código
                                    con otras personas.
                                </p>
                            </div>

                            <p style="
                                margin: 28px 0 0 0;
                                font-size: 13px;
                                line-height: 1.5;
                                color: #9ca3af;
                            ">
                                Si no realizaste esta solicitud, puedes ignorar
                                este correo.
                            </p>

                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="
                            padding: 22px 30px;
                            background-color: #f9fafb;
                            border-top: 1px solid #e5e7eb;
                            text-align: center;
                        ">
                            <p style="
                                margin: 0;
                                font-size: 12px;
                                color: #9ca3af;
                            ">
                                Este es un correo automático. Por favor,
                                no respondas a este mensaje.
                            </p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>

    </table>

</body>
</html>
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=None,
        to=[otp.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from ..otp_service import OTP_EXPIRATION_MINUTES


def send_security_otp_email(otp):

    subject = "Código de seguridad para iniciar sesión"

    logo_url = f"{settings.SITE_URL}AgroVisionAI.webp"

    text_content = f"""
Hola,

Se ha solicitado iniciar sesión en tu cuenta de AgroVisionAI.

Para completar el inicio de sesión,
introduce el siguiente código de seguridad:

{otp.code}

Este código expira en {OTP_EXPIRATION_MINUTES} minutos.

Por seguridad, no compartas este código con nadie.

Si no intentaste iniciar sesión,
te recomendamos revisar la seguridad de tu cuenta.

Saludos,
El equipo de AgroVisionAI
""".strip()

    html_content = f"""
<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>{subject}</title>
</head>

<body style="
    margin: 0;
    padding: 0;
    background-color: #f3f4f6;
    font-family: Arial, Helvetica, sans-serif;
    color: #111827;
">

    <!-- CONTENEDOR PRINCIPAL -->

    <table
        width="100%"
        cellpadding="0"
        cellspacing="0"
        border="0"
        style="
            background-color: #f3f4f6;
            padding: 20px 10px;
        "
    >

        <tr>
            <td align="center">

                <!-- CARD -->

                <table
                    width="100%"
                    cellpadding="0"
                    cellspacing="0"
                    border="0"
                    style="
                        max-width: 520px;
                        background-color: #ffffff;
                        border-radius: 14px;
                        overflow: hidden;
                    "
                >

                    <!-- HEADER -->

                    <tr>
                        <td
                            align="center"
                            style="
                                padding: 30px 25px;
                                background-color: #ffffff;
                                border-bottom: 1px solid #e5e7eb;
                            "
                        >

                            <img
                                src="{logo_url}"
                                alt="AgroVisionAI"
                                width="180"
                                style="
                                    display: block;
                                    width: 180px;
                                    max-width: 100%;
                                    height: auto;
                                    border: 0;
                                "
                            >

                        </td>
                    </tr>


                    <!-- GREEN LINE -->

                    <tr>
                        <td style="
                            height: 4px;
                            background-color: #10B981;
                            font-size: 0;
                            line-height: 0;
                        ">
                        </td>
                    </tr>


                    <!-- CONTENT -->

                    <tr>
                        <td style="
                            padding: 35px 30px 30px 30px;
                        ">

                            <!-- TITLE -->

                            <h1 style="
                                margin: 0 0 14px 0;
                                font-size: 24px;
                                line-height: 1.3;
                                font-weight: 700;
                                color: #111827;
                            ">
                                Verificación de seguridad
                            </h1>


                            <!-- DESCRIPTION -->

                            <p style="
                                margin: 0 0 25px 0;
                                font-size: 15px;
                                line-height: 1.6;
                                color: #4b5563;
                            ">
                                Se ha solicitado iniciar sesión en tu
                                cuenta de AgroVisionAI.
                            </p>


                            <p style="
                                margin: 0 0 10px 0;
                                font-size: 14px;
                                font-weight: 600;
                                color: #374151;
                            ">
                                Introduce este código para continuar:
                            </p>


                            <!-- OTP -->

                            <table
                                width="100%"
                                cellpadding="0"
                                cellspacing="0"
                                border="0"
                            >

                                <tr>
                                    <td
                                        align="center"
                                        style="
                                            padding: 20px;
                                            background-color: #ecfdf5;
                                            border: 1px solid #a7f3d0;
                                            border-radius: 10px;
                                        "
                                    >

                                        <span style="
                                            font-size: 32px;
                                            line-height: 1;
                                            font-weight: 700;
                                            letter-spacing: 8px;
                                            color: #047857;
                                        ">
                                            {otp.code}
                                        </span>

                                    </td>
                                </tr>

                            </table>


                            <!-- EXPIRATION -->

                            <p style="
                                margin: 18px 0 0 0;
                                text-align: center;
                                font-size: 13px;
                                line-height: 1.5;
                                color: #6b7280;
                            ">

                                Este código expira en

                                <strong style="
                                    color: #111827;
                                ">
                                    {OTP_EXPIRATION_MINUTES} minutos
                                </strong>.

                            </p>


                            <!-- SECURITY -->

                            <table
                                width="100%"
                                cellpadding="0"
                                cellspacing="0"
                                border="0"
                                style="
                                    margin-top: 28px;
                                "
                            >

                                <tr>
                                    <td style="
                                        padding: 15px;
                                        background-color: #f0fdf4;
                                        border-left: 4px solid #10B981;
                                        border-radius: 6px;
                                    ">

                                        <p style="
                                            margin: 0;
                                            font-size: 13px;
                                            line-height: 1.5;
                                            color: #166534;
                                        ">

                                            <strong>
                                                Importante:
                                            </strong>

                                            Por seguridad, nunca compartas
                                            este código con otras personas.

                                        </p>

                                    </td>
                                </tr>

                            </table>


                            <!-- UNKNOWN LOGIN -->

                            <p style="
                                margin: 28px 0 0 0;
                                font-size: 13px;
                                line-height: 1.6;
                                color: #9ca3af;
                            ">

                                Si no intentaste iniciar sesión,
                                te recomendamos revisar la seguridad
                                de tu cuenta.

                            </p>

                        </td>
                    </tr>


                    <!-- FOOTER -->

                    <tr>
                        <td style="
                            padding: 22px 30px;
                            background-color: #f9fafb;
                            border-top: 1px solid #e5e7eb;
                            text-align: center;
                        ">

                            <p style="
                                margin: 0 0 6px 0;
                                font-size: 13px;
                                font-weight: 600;
                                color: #374151;
                            ">
                                AgroVisionAI
                            </p>

                            <p style="
                                margin: 0;
                                font-size: 12px;
                                line-height: 1.5;
                                color: #9ca3af;
                            ">
                                Este es un correo automático.
                                Por favor, no respondas a este mensaje.
                            </p>

                        </td>
                    </tr>

                </table>

                <!-- END CARD -->

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

    email.attach_alternative(
        html_content,
        "text/html"
    )

    email.send()

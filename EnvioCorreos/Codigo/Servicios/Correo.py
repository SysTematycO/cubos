import smtplib
from email.mime.text import MIMEText

mensaje = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css?family=Poppins" rel="stylesheet">
        <style>
            .texto{ 
                font-family: 'Poppins', sans-Serif;
                font-size: 35px;
            }
        </style>
    </head>    
    <body>
        <p><img src="https://i.imgur.com/NBY5ru3.png" alt="Imagen de ejemplo"></p>
        <p class="texto">Hola,</p>
        <p>Esta es una imagen:</p>
        <p>Saludos cordiales,</p>
        <p>Tu nombre</p>
        <p><img src="https://i.imgur.com/NBY5ru3.png" alt="Imagen de ejemplo"></p>
    </body>
</html>
"""

msg = MIMEText(mensaje, 'html')
msg['Subject'] = "Prueba"
msg['From'] = "coord.cartera@deltacredit.com.co"
msg['To'] = "jcamargo@deltacredit.com.co"

usuario = "coord.cartera@deltacredit.com.co"
contraseña = "D0s0r102023*"


servidor_smtp = smtplib.SMTP('smtp.office365.com', 587)
servidor_smtp.starttls()
servidor_smtp.login(usuario, contraseña)

texto = msg.as_string()
servidor_smtp.sendmail(msg['From'], msg['To'], texto)

servidor_smtp.quit()

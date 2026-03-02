def generar_link_documentos(radicado: str) -> str:
    return f"http://localhost:8501/?formulario=2&radicado={radicado}"


def generar_email_bienvenida(nombre: str, radicado: str, link: str) -> str:

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif;">

        <h2>👋 Bienvenido(a), {nombre}</h2>

        <p>Su caso ha sido registrado exitosamente en <b>Sistema Jurídico SFD</b>.</p>

        <p><b>📌 Radicado:</b> {radicado}</p>

        <p>Para continuar con el proceso, por favor cargue los documentos en el siguiente enlace:</p>

        <p>
            <a href="{link}" style="
                background-color:#2E86C1;
                color:white;
                padding:10px 15px;
                text-decoration:none;
                border-radius:5px;
            ">
                📎 Cargar documentos
            </a>
        </p>

        <p>Este canal será utilizado para el envío de contrato y poder.</p>

        <br>

        <p>Atentamente,<br>
        <b>Sistema Jurídico SFD</b></p>

    </body>
    </html>
    """
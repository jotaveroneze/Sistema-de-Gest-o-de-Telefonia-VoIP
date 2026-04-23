import os
from flask import send_file

def obter_garantia_pdf():
    caminho_pdf = os.path.join(
        os.getcwd(),
        "static",
        "pdf",
        "garantia.pdf"
    )

    return send_file(
        caminho_pdf,
        as_attachment=False,
        mimetype="application/pdf"
    )

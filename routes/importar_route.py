from flask import Blueprint, request, jsonify, render_template_string
from flask_login import login_required

from controllers.importar_controller import importar_telefones_excel

importar_bp = Blueprint("importar", __name__, url_prefix="/importar")

@importar_bp.route('/', methods=['GET'])
@login_required
def index():
    # Formulário HTML simples para upload
    return render_template_string("""
        <h1>Importação de Telefones</h1>
        <form method="POST" action="/importar/importar" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xlsx">
            <button type="submit">Importar</button>
        </form>
    """)

# Rota POST que chama a função de importação
@importar_bp.route('/importar', methods=['POST'])
@login_required
def importar():
    # A função importar_telefones_excel já lida com a requisição e retorna o JSON
    return importar_telefones_excel()
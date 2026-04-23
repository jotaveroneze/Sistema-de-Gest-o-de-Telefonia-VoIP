import pandas as pd
import pymysql
from flask import request, send_file
from io import BytesIO

def export_excel_controller():
    try:
        # O que o usuário marcou
        selecionados = request.form.getlist("exportar")

        if not selecionados:
            return "Nenhuma opção selecionada"

        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="controletelefonepmp"
        )

        output = BytesIO()

        # Excel com múltiplas abas
        with pd.ExcelWriter(output, engine="openpyxl") as writer:

            if "usuario" in selecionados:
                df = pd.read_sql("SELECT u.*,d.nome AS departamento FROM usuario u INNER JOIN departamento d ON u.iddepartamento = d.id;", conn)
                df.to_excel(writer, sheet_name="Usuarios", index=False)

            if "telefone" in selecionados:
                df = pd.read_sql("SELECT t.id, COALESCE(m.nome, '-') AS modelo, t.patrimonio, t.serial, t.macaddress, t.nometelefone, t.processocompra, t.notafiscal, t.montado, t.patrimoniado, t.defeito, COALESCE(sec.sigla, '-') AS secretaria, COALESCE(dep.nome, '-') AS departamento, COALESCE(lt.endereco, '-') AS endereco, COALESCE(lt.nomelugar, '-') AS lugartelefone, COALESCE(lt.andar, '-') AS andar, COALESCE(GROUP_CONCAT(DISTINCT p.nome SEPARATOR ', '), '-') AS pessoas, COALESCE(GROUP_CONCAT(DISTINCT p.funcional SEPARATOR ', '), '-') AS funcionais, COALESCE(GROUP_CONCAT(DISTINCT p.cpf SEPARATOR ', '), '-') AS cpfs, COALESCE(GROUP_CONCAT(DISTINCT r.numero SEPARATOR ', '), '-') AS ramais FROM telefone t LEFT JOIN modelo m ON m.id = t.idmodelo LEFT JOIN lugartelefone lt ON lt.id = t.idlugartelefone LEFT JOIN departamento dep ON dep.id = lt.iddepartamento LEFT JOIN secretaria sec ON sec.id = dep.idsecretaria LEFT JOIN pessoatelefone pt ON pt.idtelefone = t.id LEFT JOIN pessoa p ON p.id = pt.idpessoa LEFT JOIN telefoneramal tr ON tr.idtelefone = t.id LEFT JOIN ramal r ON r.id = tr.idramal WHERE t.status = 1 GROUP BY t.id;", conn)
                df.to_excel(writer, sheet_name="Telefones", index=False)

            if "modelo" in selecionados:
                df = pd.read_sql("SELECT * FROM modelo", conn)
                df.to_excel(writer, sheet_name="Modelos", index=False)

            if "ramal" in selecionados:
                df = pd.read_sql("SELECT r.*, t.*, o.* FROM ramal r INNER JOIN tronco t ON r.idtronco = t.id INNER JOIN operadora o ON t.idoperadora = o.id;", conn)
                df.to_excel(writer, sheet_name="Ramais", index=False)

            if "numerogrupo" in selecionados:
                df = pd.read_sql("SELECT u.*,d.nome AS departamento FROM numerodegrupo u INNER JOIN departamento d ON u.iddepartamento = d.id;", conn)
                df.to_excel(writer, sheet_name="Numero_Grupo", index=False)

            if "tronco" in selecionados:
                df = pd.read_sql("SELECT u.*,d.nome AS operadora FROM tronco u INNER JOIN operadora d ON u.idoperadora = d.id;", conn)
                df.to_excel(writer, sheet_name="Tronco", index=False)

            if "pessoa" in selecionados:
                df = pd.read_sql("SELECT u.*,v.nome AS vinculo, s.nome AS secretaria, d.nome AS departamento, e.nome AS empresa FROM pessoa u INNER JOIN vinculo v ON u.idvinculo = v.id INNER JOIN secretaria s ON u.idsecretaria = s.id INNER JOIN departamento d ON u.iddepartamento = d.id INNER JOIN empresa e ON u.idempresa = e.id;", conn)
                df.to_excel(writer, sheet_name="Pessoas", index=False)

            if "departamento" in selecionados:
                df = pd.read_sql("SELECT u.*,d.nome AS secretaria FROM departamento u INNER JOIN secretaria d ON u.idsecretaria = d.id;", conn)
                df.to_excel(writer, sheet_name="Departamentos", index=False)

            if "empresa" in selecionados:
                df = pd.read_sql("SELECT * FROM empresa", conn)
                df.to_excel(writer, sheet_name="Empresas", index=False)

        conn.close()

        output.seek(0)

        return send_file(
            output,
            download_name="exportacao_dados.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return f"Erro ao exportar Excel: {str(e)}"

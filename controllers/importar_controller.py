from datetime import datetime

import pandas as pd
from flask import request, jsonify
from extensions import db
from models.grupocaptura_model import Grupocaptura
from models.numerogrupo_model import Numerogrupo
from models.operadora_model import Operadora
from models.pessoatelefone_model import PessoaTelefone
from models.ramal_model import Ramal
from models.ramalnumerogrupo_model import RamalNumeroGrupo
from models.secretaria_model import Secretaria
from models.departamento_model import Departamento
from models.modelo_model import Modelo
from models.telefone_model import Telefone
from models.lugartelefone_model import LugarTelefone
from models.pessoa_model import Pessoa
from models.telefoneramal_model import TelefoneRamal
from models.tronco_model import Tronco
from models.vinculo_model import Vinculo
from models.empresa_model import Empresa
from models.entregas_model import Entregas
import sqlalchemy.orm

# Importe seus modelos aqui
# from models import Telefone, Modelo, LugarTelefone, Departamento, Secretaria

def importar_telefones_excel():
    """
    Função Flask para importar telefones de um arquivo Excel.
    Verifica a existência de registros relacionados e os cria se necessário.
    """
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    try:
        # Lendo o arquivo Excel
        df = pd.read_excel(file)

        telefones_importados = 0
        erros = []

        for index, row in df.iterrows():
            try:
                # 1. Verificar/Criar Secretaria
                secretaria = Secretaria.query.filter_by(sigla=row['secretaria_sigla']).first()
                if not secretaria:
                    secretaria = Secretaria(
                        nome=row['secretaria_nome'],
                        sigla=row['secretaria_sigla']
                    )
                    db.session.add(secretaria)
                    db.session.flush()  # Para obter o ID

                # 2. Verificar/Criar Departamento
                departamento = Departamento.query.filter_by(
                    nome=row['departamento_nome'],
                    idsecretaria=secretaria.id
                ).first()
                if not departamento:
                    departamento = Departamento(
                        nome=row['departamento_nome'],
                        idsecretaria=secretaria.id
                    )
                    db.session.add(departamento)
                    db.session.flush()

                # 3. Verificar/Criar LugarTelefone
                lugar = LugarTelefone.query.filter_by(
                    nomelugar=row['lugar_nome'],
                    andar=row['lugar_andar'],
                    endereco=row['lugar_endereco'],
                    iddepartamento=departamento.id
                ).first()
                if not lugar:
                    lugar = LugarTelefone(
                        nomelugar=row['lugar_nome'],
                        andar=row['lugar_andar'],
                        endereco=row['lugar_endereco'],
                        iddepartamento=departamento.id
                    )
                    db.session.add(lugar)
                    db.session.flush()

                # 4. Verificar/Criar Modelo
                modelo = Modelo.query.filter_by(nome=row['modelo_nome']).first()
                if not modelo:
                    modelo = Modelo(nome=row['modelo_nome'])
                    db.session.add(modelo)
                    db.session.flush()

                # Verificar/Criar Vinculo
                vinculo = Vinculo.query.filter_by(nome=row['vinculo_nome']).first()
                if not vinculo:
                    vinculo = Vinculo(nome=row['vinculo_nome'])
                    db.session.add(vinculo)
                    db.session.flush()

                # Verificar/Criar empresa
                empresa = Empresa.query.filter_by(nome=row['empresa_nome']).first()
                if not empresa:
                    empresa = Empresa(
                        nome=row['empresa_nome'],
                        status=1
                    )
                    db.session.add(empresa)
                    db.session.flush()

                cpf = row['pessoa_cpf']
                funcional = row['pessoa_funcional']

                # Normalizar CPF
                if pd.isna(cpf) or str(cpf).lower() == 'nan':
                    cpf = None
                else:
                    cpf = str(cpf).strip()

                # Normalizar Funcional
                if pd.isna(funcional) or str(funcional).lower() == 'nan':
                    funcional = None
                else:
                    funcional = str(funcional)

                # Verificar/Criar Pessoa
                pessoa = None  # Inicializa a variável
                query = Pessoa.query
                if cpf:
                    query = query.filter(Pessoa.cpf == cpf)
                elif funcional:
                    query = query.filter(Pessoa.funcional == funcional)
                else:
                    query = None

                pessoa_existente = query.first() if query else None

                if not pessoa_existente:
                    nova_pessoa = Pessoa(
                        nome=row['pessoa_nome'],
                        funcional=funcional,
                        cpf=cpf,
                        status=1,
                        idvinculo=vinculo.id,
                        iddepartamento=departamento.id,
                        idempresa=empresa.id
                    )
                    db.session.add(nova_pessoa)
                    db.session.flush()  # Garante que o ID da nova pessoa seja gerado
                    pessoa = nova_pessoa
                else:
                    # Atualiza os dados da pessoa existente, se necessário
                    pessoa_existente.nome = row['pessoa_nome']
                    pessoa_existente.idvinculo = vinculo.id
                    pessoa_existente.iddepartamento = departamento.id
                    pessoa_existente.idempresa = empresa.id
                    pessoa = pessoa_existente
                    # ==========================================================
                    # 1. ADICIONAR LÓGICA PARA GRUPO DE CAPTURA
                    # ==========================================================
                    # Supondo que sua planilha tenha uma coluna 'grupocaptura_nome'
                    nome_grupo_captura = row.get('grupocaptura_nome')
                    grupocaptura = None  # Inicializa a variável

                    # Só processa se o nome do grupo de captura for fornecido na planilha
                    if pd.notna(nome_grupo_captura) and nome_grupo_captura.strip():
                        # Busca o grupo de captura pelo nome
                        grupocaptura = Grupocaptura.query.filter_by(nome=nome_grupo_captura.strip()).first()

                        # Se não encontrar, cria um novo
                        if not grupocaptura:
                            grupocaptura = Grupocaptura(
                                nome=nome_grupo_captura.strip(),
                                status=1
                            )
                            db.session.add(grupocaptura)
                            db.session.flush()  # Garante que o ID seja gerado para uso posterior

                # 5. Verificar se o Telefone já existe (pelo serial ou macaddress ou patrimonio)
                telefone_existente = Telefone.query.filter(
                    (Telefone.serial == str(row['serial'])) |
                    (Telefone.macaddress == str(row['macaddress'])) |
                    (Telefone.patrimonio == row['patrimonio'])
                ).first()

                novo_telefone = None

                if not telefone_existente:
                    novo_telefone = Telefone(
                        nometelefone=row['nometelefone'],
                        patrimonio=row['patrimonio'],
                        serial=str(row['serial']),
                        macaddress=str(row['macaddress']),
                        processocompra=row['processocompra'],
                        notafiscal=row['notafiscal'],
                        idmodelo=modelo.id,
                        idlugartelefone=lugar.id,
                        status=1,
                        montado=row['montado'],
                        patrimoniado=row['patrimoniado'],
                        defeito=row['defeito']
                    )
                    db.session.add(novo_telefone)
                    db.session.flush()
                    telefones_importados += 1
                else:
                    # Atualizar dados do telefone existente
                    telefone_existente.nometelefone = row['nometelefone']
                    telefone_existente.processocompra = row['processocompra']
                    telefone_existente.notafiscal = row['notafiscal']
                    telefone_existente.idmodelo = modelo.id
                    telefone_existente.idlugartelefone = lugar.id

                    # Flags de controle (mantendo padrão do sistema)
                    telefone_existente.status = 1
                    telefone_existente.montado = row['montado']
                    telefone_existente.patrimoniado = row['patrimoniado']
                    telefone_existente.defeito = row['defeito']

                telefone = novo_telefone if not telefone_existente else telefone_existente


                # Verifica/Cria Pessoa Telefone
                with db.session.no_autoflush:
                    vinculo_pessoa_telefone = PessoaTelefone.query.filter_by(
                        idpessoa=pessoa.id,
                        idtelefone=telefone.id
                    ).first()

                if not vinculo_pessoa_telefone:
                    db.session.add(PessoaTelefone(
                        idpessoa=pessoa.id,
                        idtelefone=telefone.id,
                    ))

                # Verificar/Criar número de grupo
                numero_grupo_excel = row['numerogrupo_numero']
                descricao = row['numerogrupo_descricao']

                if pd.isna(descricao):
                    descricao = None

                if pd.isna(descricao):
                    descricao = None
                if pd.isna(numero_grupo_excel):
                    numerogrupo = None
                else:
                    numerogrupo = Numerogrupo.query.filter_by(
                        numero=int(numero_grupo_excel),
                        iddepartamento=departamento.id
                    ).first()

                    if not numerogrupo:
                        numerogrupo = Numerogrupo(
                            numero=int(numero_grupo_excel),
                            descricao=descricao,
                            gravado=0,
                            status=1,
                            iddepartamento=departamento.id
                        )
                        db.session.add(numerogrupo)
                        db.session.flush()


                # Verificar/Criar operadora
                operadora = Operadora.query.filter_by(
                    nome=row['operadora_nome'],
                    contrato=row['operadora_contrato']
                ).first()

                if not operadora:
                    operadora = Operadora(
                        nome=row['operadora_nome'],
                        contrato=row['operadora_contrato'],
                        processo=row['operadora_processo'],
                        status=1
                    )
                    db.session.add(operadora)
                    db.session.flush()

                # Verificar/Criar tronco
                tronco = Tronco.query.filter_by(
                    numerochave=row['tronco_numerochave'],
                    idoperadora=operadora.id
                ).first()

                if not tronco:
                    tronco = Tronco(
                        numerochave=row['tronco_numerochave'],
                        ramalinicial=row['tronco_ramalinicial'],
                        ramalfinal=row['tronco_ramalfinal'],
                        idoperadora=operadora.id,
                        status=1
                    )
                    db.session.add(tronco)
                    db.session.flush()

                # Verificar/Criar ramal
                ramal = Ramal.query.filter_by(
                    numero=row['ramal_numero'],
                    idtronco=tronco.id
                ).first()

                # Obter o ID do grupo de captura, se ele foi encontrado ou criado
                id_grupocaptura = grupocaptura.id if grupocaptura else None

                if not ramal:
                    ramal = Ramal(
                        numero=row['ramal_numero'],
                        idtronco=tronco.id,
                        idgrupocaptura=id_grupocaptura,
                        status=1,
                        gravado=0
                    )
                    db.session.add(ramal)
                    db.session.flush()

                # Verificar/Criar ramal x numero de grupo
                if numerogrupo:
                    with db.session.no_autoflush:
                        vinculo_ramal_grupo = RamalNumeroGrupo.query.filter_by(
                            idramal=ramal.id,
                            idnumerogrupo=numerogrupo.id
                        ).first()

                    if not vinculo_ramal_grupo:
                        db.session.add(RamalNumeroGrupo(
                            idramal=ramal.id,
                            idnumerogrupo=numerogrupo.id
                        ))

                # Verificar/Criar ramal x telefone
                with db.session.no_autoflush:
                    vinculo_telefone_ramal = TelefoneRamal.query.filter_by(
                        idtelefone=telefone.id,
                        idramal=ramal.id
                    ).first()

                if not vinculo_telefone_ramal:
                    db.session.add(TelefoneRamal(
                        idtelefone=telefone.id,
                        idramal=ramal.id,
                    ))
                else:
                    vinculo_telefone_ramal.dataalteracao = datetime.utcnow()

                # =========================
                # REGISTRAR ENTREGA
                # =========================
                data_entrega_excel = row.get('data_entrega')

                # Normalizar data de entrega
                data_entrega = None
                if not pd.isna(data_entrega_excel):
                    if isinstance(data_entrega_excel, datetime):
                        data_entrega = data_entrega_excel.date()
                    else:
                        data_entrega = pd.to_datetime(data_entrega_excel).date()

                # 👉 SÓ CONTINUA SE EXISTIR DATA DE ENTREGA
                if data_entrega:
                    # Verificar se já existe entrega ativa para este telefone
                    with db.session.no_autoflush:
                        entrega_existente = Entregas.query.filter_by(
                            idtelefone=telefone.id,
                            idpessoa=pessoa.id,
                            status=1
                        ).first()

                    if not entrega_existente:
                        entrega = Entregas(
                            dataentrega=data_entrega,
                            iddepartamento=departamento.id,
                            idpessoa=pessoa.id,
                            idtelefone=telefone.id,
                            idlugartelefone=lugar.id,
                            status=1
                        )
                        db.session.add(entrega)

                    # 📌 EXISTE DATA → TELEFONE ENTREGUE/MONTADO
                    telefone.montado = 1
            except Exception as e:
                db.session.rollback()
                erros.append(f"Erro na linha {index + 2}: {str(e)}")
                continue

        db.session.commit()
        return jsonify({
            "message": "Processamento concluído",
            "importados": telefones_importados,
            "erros": erros
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao processar arquivo: {str(e)}"}), 500

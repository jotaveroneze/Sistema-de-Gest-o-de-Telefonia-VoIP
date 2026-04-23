async function visualizarPessoasDoRamal(idRamal, numeroRamal) {
    try {
        idRamalAtual = idRamal;
        numeroRamalAtual = numeroRamal;
        // Atualiza o label do ramal
        document.getElementById("labelNumeroRamal").innerText = numeroRamalAtual;

        // Busca pessoas vinculadas ao ramal
        const response = await fetch(`telefoneramal/listar/${idRamal}/pessoas`);
        if (!response.ok) {
            throw new Error("Erro ao buscar pessoas do ramal");
        }

        const pessoas = await response.json();

        // Preenche a tabela
        preencherTabelaPessoasRamal(pessoas);

        // Abre o modal
        const modal = new bootstrap.Modal(
            document.getElementById("modalVisualizarPessoasRamal")
        );
        modal.show();

    } catch (error) {
        console.error(error);
        alert("Erro ao carregar pessoas vinculadas ao ramal.");
    }
}

function preencherTabelaPessoasRamal(lista) {
    const tbody = document.querySelector("#tabelaPessoasRamal tbody");
    tbody.innerHTML = "";

    if (!lista || lista.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    Nenhum telefone vinculado a este ramal
                </td>
            </tr>
        `;
        return;
    }

    lista.forEach(telefone => {

        // 🔹 TELEFONE SEM PESSOA
        if (!telefone.pessoas || telefone.pessoas.length === 0) {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${telefone.patrimonio || "-"}</td>
                <td>${telefone.serial || "-"}</td>
                <td colspan="3" class="text-center text-muted">
                    Sem pessoa vinculada
                </td>
                <td class="text-center">
                    <button class="btn btn-outline-danger btn-sm"
                        title="Desvincular telefone do ramal"
                        onclick="removerTelefoneDoRamal(${telefone.idtelefoneramal})">
                        <i class="fa-solid fa-link-slash"></i>
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
            return;
        }

        // 🔹 TELEFONE COM PESSOAS
        telefone.pessoas.forEach((pessoa, index) => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                ${index === 0 ? `
                    <td rowspan="${telefone.pessoas.length}">
                        ${telefone.patrimonio || "-"}
                    </td>
                    <td rowspan="${telefone.pessoas.length}">
                        ${telefone.serial || "-"}
                    </td>
                ` : ""}

                <td>
                    <strong>${pessoa.nome || "-"}</strong><br>
                    <small class="text-muted">
                        ${pessoa.secretaria || "-"} / ${pessoa.departamento || "-"}
                    </small>
                </td>
                <td>${pessoa.funcional || "-"}</td>
                <td>${pessoa.cpf || "-"}</td>


                ${index === 0 ? `
                    <td rowspan="${telefone.pessoas.length}" class="text-center align-middle">
                        <button class="btn btn-outline-danger btn-sm"
                            title="Desvincular telefone do ramal"
                            onclick="removerTelefoneDoRamal(${telefone.idtelefoneramal})">
                            <i class="fa-solid fa-link-slash"></i>
                        </button>
                    </td>
                ` : ""}
            `;

            tbody.appendChild(tr);
        });
    });
}


async function removerTelefoneDoRamal(idTelefoneRamal) {
    if (!confirm("Deseja remover este telefone do ramal?")) return;

    try {
        const response = await fetch(
            `/telefoneramal/remover/${idTelefoneRamal}`,
            { method: "DELETE" }
        );

        if (!response.ok) {
            throw new Error("Erro ao remover telefone do ramal");
        }

        alert("Telefone removido do ramal com sucesso!");

        visualizarPessoasDoRamal(idRamalAtual, numeroRamalAtual);

    } catch (error) {
        console.error(error);
        alert("Erro ao remover telefone do ramal");
    }
}


// ===============================
// ABRIR MODAL
// ===============================
async function abrirModalAdicionarPessoaRamal(idRamal, numeroRamal) {

    // 🔥 DEFINIR O RAMAL AQUI

    telefonesSelecionados.clear();

    document.getElementById("labelRamalAdicionarPessoa").innerText = numeroRamalAtual;

    await carregarTelefonesPessoa();

    abrirModal("modalAdicionarPessoaRamal");
}



// ===============================
// CARREGAR PESSOAS
// ===============================

async function carregarTelefonesPessoa() {
    try {
        const response = await fetch(
            `/telefoneramal/${idRamalAtual}/telefones-disponiveis`
        );

        if (!response.ok) throw new Error("Erro ao buscar telefones");

        telefones = await response.json();
        preencherTabelaAdicionarTelefonePessoa(telefones);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar telefones");
    }
}

function preencherTabelaAdicionarTelefonePessoa(lista) {
    const tbody = document.querySelector("#tabelaAdicionarTelefoneRamal tbody");
    if (!tbody) return;

    tbody.innerHTML = "";

    if (!lista || lista.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    Nenhum telefone disponível
                </td>
            </tr>
        `;
        return;
    }

    lista.forEach(t => {
        const checked = telefonesSelecionados.has(t.id) ? "checked" : "";

        // monta as pessoas vinculadas ao telefone
        const pessoasHtml = (t.pessoas && t.pessoas.length)
            ? t.pessoas.map(p =>
                `<div>
                    <strong>
                    ${p.secretaria || "-"}<br>
                    ${p.departamento || "-"}<br></strong>
                    ${p.nome}<br>
                    Funcional: ${p.funcional || "-"}<br>
                    CPF: ${p.cpf || "-"}<br>

                </div>`
              ).join("<hr class='my-1'>")
            : "<span class='text-muted'>Sem pessoas</span>";

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="text-center">
                <input type="checkbox"
                       ${checked}
                       onchange="selecionarTelefone(${t.id}, this)">
            </td>
            <td>${t.patrimonio || "-"}</td>
            <td>${t.serial || "-"}</td>
            <td>${pessoasHtml}</td>
        `;

        tbody.appendChild(tr);
    });
}

function selecionarTelefone(idTelefone, checkbox) {
    if (checkbox.checked) {
        telefonesSelecionados.add(idTelefone);
    } else {
        telefonesSelecionados.delete(idTelefone);
    }
}


document.getElementById("searchTelefoneAdicionarRamal")
    ?.addEventListener("input", function () {
        const texto = this.value.toLowerCase();

        const filtrados = telefones.filter(t =>
            String(t.serial || "").toLowerCase().includes(texto) ||
            String(t.patrimonio || "").includes(texto)
        );

        preencherTabelaAdicionarTelefonePessoa(filtrados);
    });


async function salvarTelefoneRamal() {

    if (!idRamalAtual) {
        alert("Ramal não selecionado");
        return;
    }

    if (telefonesSelecionados.size === 0) {
        alert("Selecione ao menos um telefone");
        return;
    }

    try {
        const response = await fetch("/telefoneramal/vincular_telefones", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                idramal: idRamalAtual,
                telefones: Array.from(telefonesSelecionados)
            })
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.erro);

        alert("Telefone(s) vinculados ao ramal com sucesso!");

        fecharModaisVinculo();
        telefonesSelecionados.clear();
        visualizarPessoasDoRamal(idRamalAtual, numeroRamalAtual);

        window.location.href = '/telefone'

    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}


//TELA TELEFONES
async function abrirVincularRamalTelefone(idTelefone, textoTelefone, serial) {

    telefoneAtivoId = idTelefone;
    telefoneAtivoTexto = textoTelefone;
    telefoneAtivoSerialTexto = serial;

    // Labels do modal
    document.getElementById("labelTelefoneRamal").innerText = textoTelefone;
    document.getElementById("labelTelefoneSerialRamal").innerText = serial;

    const tbody = document.getElementById("tbodyRamaisTelefone");
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-muted">Carregando...</td>
            </tr>
        `;
    }

    const modalElement = document.getElementById("modalVisualizarRamaisTelefone");

    if (!modalVisualizarRamaisTelefoneInstance) {
        modalVisualizarRamaisTelefoneInstance = new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
    }

    modalVisualizarRamaisTelefoneInstance.show();

    try {
        await carregarRamaisVinculadosTelefone(idTelefone);
    } catch (e) {
        console.error(e);
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center text-danger">
                        Erro ao carregar ramais
                    </td>
                </tr>
            `;
        }
    }
}


async function carregarRamaisVinculadosTelefone(idTelefone) {
    try {
        const response = await fetch(`/telefoneramal/listar_por_telefone/${idTelefone}`);
        if (!response.ok) throw new Error("Erro ao buscar ramais vinculados");

        const dados = await response.json();
        preencherTabelaRamaisVinculados(dados);

    } catch (e) {
        console.error(e);
        alert("Erro ao carregar ramais vinculados");
    }
}

function preencherTabelaRamaisVinculados(lista) {
    const tbody = document.querySelector("#tabelaRamaisTelefone tbody");
    tbody.innerHTML = "";

    if (!lista.length) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">Nenhum ramal vinculado</td></tr>`;
        return;
    }

    lista.forEach(r => {
        tbody.innerHTML += `
            <tr>
                <td>${r.numero}</td>
                <td>
                    ${r.gravado
                        ? `<i class="fa-solid fa-microphone text-success"></i>`
                        : `<i class="fa-solid fa-microphone-slash text-danger"></i>`
                    }
                </td>
                <td>

                <button class="btn btn-outline-danger btn-sm"
                        title="Desvincular ramal"
                        onclick="removerRamalTelefone(${r.id})">
                    <i class="fa-solid fa-unlink"></i>
                </button>
                </td>
            </tr>
        `;
    });
}

function abrirModalAdicionarRamalTelefone() {
    document.getElementById("labelTelefoneAdicionarRamal").innerText = telefoneAtivoTexto;
    document.getElementById("labelTelefoneSerialAdicionarRamal").innerText = telefoneAtivoSerialTexto;

    carregarRamaisParaVinculoTelefone(telefoneAtivoId);

    abrirModal("modalAdicionarRamalTelefone");
}

async function carregarRamaisParaVinculoTelefone(idTelefone) {
    try {
        const response = await fetch(`/telefoneramal/listar_disponiveis_para_telefone/${telefoneAtivoId}`);
        if (!response.ok) throw new Error("Erro ao buscar ramais disponíveis");

        const dados = await response.json();
        preencherTabelaAdicionarRamalTelefone(dados);

    } catch (e) {
        console.error(e);
        alert("Erro ao carregar ramais disponíveis");
    }
}

function preencherTabelaAdicionarRamalTelefone(lista) {
    const tbody = document.querySelector("#tabelaAdicionarRamalTelefone tbody");
    tbody.innerHTML = "";

    if (!lista.length) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">Nenhum ramal disponível</td></tr>`;
        return;
    }

    lista.forEach(r => {
        tbody.innerHTML += `
            <tr>
                <td class="text-center">
                <input type="checkbox" value="${r.id}">
                </td>
                <td>${r.numero}</td>
                <td>${r.em_uso ? "Em uso" : "Livre"}</td>
                <td>
                    ${r.gravado
                        ? `<i class="fa-solid fa-microphone text-success"></i>`
                        : `<i class="fa-solid fa-microphone-slash text-danger"></i>`
                    }
                </td>
            </tr>
        `;
    });
}

async function salvarRamalTelefone() {
    const checkboxes = document.querySelectorAll(
        "#tabelaAdicionarRamalTelefone tbody input[type=checkbox]:checked"
    );

    const ramaisSelecionados = Array.from(checkboxes).map(cb => parseInt(cb.value));

    if (!ramaisSelecionados.length) {
        alert("Selecione pelo menos um ramal!");
        return;
    }

    try {
        const response = await fetch("/telefoneramal/vincular", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id_telefone: telefoneAtivoId,
                ramais: ramaisSelecionados
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.erro || "Erro ao vincular ramais");
            return;
        }

        alert(data.mensagem);

        fecharModaisVinculo();
        // atualiza tabela de ramais vinculados
        abrirVincularRamalTelefone(telefoneAtivoId, telefoneAtivoTexto);

    } catch (e) {
        console.error(e);
        alert("Erro ao vincular ramais");
    }
}

async function removerRamalTelefone(idVinculo) {
    if (!confirm("Deseja realmente desvincular este ramal do telefone?")) return;

    try {
        const response = await fetch(`/telefoneramal/${idVinculo}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.erro || "Erro ao desvincular ramal");
            return;
        }

        alert(data.mensagem);

        // atualiza tabela de ramais vinculados
        abrirVincularRamalTelefone(telefoneAtivoId, telefoneAtivoTexto);

    } catch (e) {
        console.error(e);
        alert("Erro ao desvincular ramal");
    }
}

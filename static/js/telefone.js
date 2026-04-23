/* 🔄 CARREGAR TELEFONES */
async function carregarTelefones(page = 1) {
    mostrarLoadingTabela();
    try {
        const searchInput = document.getElementById("searchTelefone");
        const searchTerm = searchInput ? searchInput.value.trim() : '';

        const params = new URLSearchParams({
            page: page,
            per_page_TELEFONES: 5  // ✅ Igual pessoa!
        });
        if (searchTerm) params.append('search', searchTerm);

        const response = await fetch(`/telefone/listar?${params}`);
        if (!response.ok) throw new Error("Erro ao buscar telefones");

        const data = await response.json();
        telefones = data.telefones;  // ✅ data.telefones (array!)
        paginaAtual = data.page;

        preencherTabelaTelefones(telefones);


        // ✅ Paginação (igual pessoa.js)
        const btnAnterior = document.getElementById('btnAnteriorTelefone');
        const btnProxima = document.getElementById('btnProximaTelefone');
        const infoPaginacao = document.getElementById('infoPaginacaoTelefone');

        if (btnAnterior) btnAnterior.disabled = !data.has_prev;
        if (btnProxima) btnProxima.disabled = !data.has_next;
        if (infoPaginacao) {
            infoPaginacao.textContent = `Página ${data.page} de ${data.pages} (${data.total})`;
        }


        // Se tiver lista de páginas
        const listaPaginas = document.getElementById('listaPaginasTelefone');
        if (listaPaginas) {
            renderizarPaginasTelefone(data.page, data.pages);
            atualizarBotoesPuloTelefone(data.page, data.pages);
        }

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar telefones");
    } finally {
        esconderLoadingTabela();
    }
}

function atualizarBotoesPuloTelefone(paginaAtual, totalPaginas) {
    const btnRetroceder = document.getElementById('btnRetrocederTelefone');
    const btnAvancar = document.getElementById('btnAvancarTelefone');

    if (btnRetroceder) {
        btnRetroceder.disabled = paginaAtual <= 10;
        btnRetroceder.onclick = () => carregarTelefones(Math.max(1, paginaAtual - 10));
    }

    if (btnAvancar) {
        btnAvancar.disabled = paginaAtual >= totalPaginas - 10;
        btnAvancar.onclick = () => carregarTelefones(Math.min(totalPaginas, paginaAtual + 10));
    }
}

function renderizarPaginasTelefone(paginaAtual, totalPaginas) {
    const ul = document.getElementById('listaPaginasTelefone');
    if (!ul) return;
    ul.innerHTML = '';

    if (totalPaginas <= 1) return;

    adicionarPaginaTelefone(ul, 1, paginaAtual);
    if (paginaAtual > 3) {
        const li = document.createElement('li');
        li.className = 'page-item disabled';
        li.innerHTML = '<span class="page-link">...</span>';
        ul.appendChild(li);
    }

    for (let p = Math.max(2, paginaAtual - 2); p <= Math.min(totalPaginas - 1, paginaAtual + 2); p++) {
        adicionarPaginaTelefone(ul, p, paginaAtual);
    }

    if (paginaAtual < totalPaginas - 2) {
        const li = document.createElement('li');
        li.className = 'page-item disabled';
        li.innerHTML = '<span class="page-link">...</span>';
        ul.appendChild(li);
    }
    adicionarPaginaTelefone(ul, totalPaginas, paginaAtual);
}

function adicionarPaginaTelefone(ul, pagina, atual) {
    const li = document.createElement('li');
    li.className = 'page-item' + (pagina === atual ? ' active' : '');
    li.innerHTML = `<button class="page-link">${pagina}</button>`;
    li.querySelector('button').onclick = () => carregarTelefones(pagina);
    ul.appendChild(li);
}

async function carregarTodasTelefones() {
    try {
        const res = await fetch('/telefone/todas');
        todasTelefones = await res.json();
    } catch(e) {
        console.warn('Não carregou todas:', e);
    }
}

/* 📋 PREENCHER TABELA */
function preencherTabelaTelefones(lista) {
    const tbody = document.getElementById("tabelaTelefones");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!lista || lista.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="10" class="text-center text-muted">Nenhum telefone encontrado</td></tr>
        `;
        return;
    }

    lista.forEach(t => {
        // ✅ SEU CÓDIGO COMPLETO INTACTOOOO (rowspan, badges, etc.)
        const pessoas = t.pessoas || [""];
        const funcionais = t.funcionais || [""];
        const cpfs = t.cpfs || [""];
        const ramais = t.ramais || [""];
        const maxLinhas = Math.max(pessoas.length, funcionais.length, cpfs.length, ramais.length);

        for (let i = 0; i < maxLinhas; i++) {
            const tr = document.createElement("tr");
            tr.classList.add("hover-highlight");

            tr.innerHTML = `
            ${i === 0 ? `
            <td rowspan="${maxLinhas}" class="text-center align-middle">
                <input type="checkbox" class="form-check-input checkbox-telefone" value="${t.id}">
            </td>
            <td rowspan="${maxLinhas}" style="font-size:0.9rem;">
                📌 Patrimônio: <strong>${t.patrimonio || "-"}</strong><br>
                🔑 Serial: <strong>${t.serial || "-"}</strong><br>
                💻 MAC: <strong>${t.macaddress || "-"}</strong><br>
                🖥️ Modelo: ${t.modelo || "-"}
            </td>
            <td rowspan="${maxLinhas}" style="font-size:0.85rem; background:#f9f9f9; padding:4px; border-radius:6px;">
                🏛️ ${t.secretaria || "-"}<br>🏢 ${t.departamento || "-"}<br>
                📍 ${t.endereco || "-"}<br>📌 ${t.lugartelefone || "-"}<br>⬆️ ${t.andar || "-"}
            </td>` : ""}
            <td><span class="badge bg-primary">${ramais[i] || "-"}</span></td>
            <td><span class="badge bg-info text-dark">${pessoas[i] || "-"}</span></td>
            <td><span class="badge bg-secondary">${funcionais[i] || "-"}</span></td>
            <td><span class="badge bg-secondary">${cpfs[i] || "-"}</span></td>
            ${i === 0 ? `
            <td rowspan="${maxLinhas}" style="font-size:0.85rem;">
                <strong>Entregue:</strong> <span class="badge ${t.entregue ? 'bg-success' : 'bg-danger'}">${t.entregue ? 'Sim' : 'Não'}</span><br>
                <strong>Data:</strong> ${t.entregue || '-'}<br>
                <strong>Patrimoniado:</strong> <span class="badge ${t.patrimoniado ? 'bg-success' : 'bg-warning text-dark'}">${t.patrimoniado ? 'Sim' : 'Não'}</span><br>
                <strong>Defeito:</strong> <span class="badge ${t.defeito ? 'bg-danger' : 'bg-success'}">${t.defeito ? 'Sim' : 'Não'}</span><br>
                <strong>Última alt.:</strong> ${t.ultimaalteracao || '-'}
            </td>
            <td rowspan="${maxLinhas}">
                <button class="btn btn-primary btn-sm" onclick="entregarTelefone(${t.id}, ${t.idpessoas?.[0]||0}, ${t.iddepartamento||0}, ${t.idlugartelefone||0})">
                    <i class="fa-solid fa-box-open"></i>
                </button>
                <!-- seus botões intactos -->
                <button class="btn btn-success btn-sm me-1" onclick="visualizarPessoasTelefone(${t.id}, '${t.patrimonio}', '${t.serial}')"><i class="fa-solid fa-user-plus"></i></button>
                <button class="btn btn-secondary btn-sm me-1" onclick="abrirVincularRamalTelefone(${t.id}, '${t.patrimonio}', '${t.serial}')"><i class="fa-solid fa-network-wired"></i></button>
                <button class="btn btn-warning btn-sm me-1" onclick="abrirEditarTelefone(${t.id})"><i class="fa-solid fa-pen"></i></button>
                <button class="btn btn-danger btn-sm" onclick="removerTelefone(${t.id})"><i class="fa-solid fa-trash"></i></button>
            </td>` : ""}
            `;
            tbody.appendChild(tr);
        }
    });

    // 🔹 Inicializa tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
}

function debounce(func, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

/* 🔍 FILTRO DE BUSCA */
document.getElementById("searchTelefone")?.addEventListener("input", debounce(function() {
    paginaAtual = 1;
    carregarTelefones(1);
}, 300));

document.getElementById('btnAnteriorTelefone')?.addEventListener('click', () => carregarTelefones(paginaAtual - 1));
document.getElementById('btnProximaTelefone')?.addEventListener('click', () => carregarTelefones(paginaAtual + 1));

/* 🗑 REMOVER TELEFONE */
async function removerTelefone(id) {
    if (!confirm("Deseja realmente excluir este telefone?")) return;

    try {
        const response = await fetch(`/telefone/remover_telefone/${id}`, {
            method: "DELETE"
        });

        if (!response.ok) throw new Error();

        carregarTelefones();

    } catch (err) {
        console.error(err);
        alert("Erro ao remover telefone");
    }
}

const searchInput = document.getElementById("searchTelefone");
const filtroPatrimoniado = document.getElementById("filtroPatrimoniado");
const filtroDefeito = document.getElementById("filtroDefeito");

function atualizarTabela() {
    const query = searchInput.value.toLowerCase();
    const montado = filtroMontado.value;
    const patrimoniado = filtroPatrimoniado.value;
    const defeito = filtroDefeito.value;

    const listaFiltrada = telefones.filter(t => {
        // 🔹 Busca por texto
    // Normaliza texto para busca (null-safe)
    const includes = (valor) =>
        valor !== null &&
        valor !== undefined &&
        valor.toString().toLowerCase().includes(query);

    // Normaliza booleanos (null-safe)
    const matchBool = (campo, filtro) =>
        filtro === "" || (campo !== null && String(campo) === filtro);

    // =========================
    // FILTRO PRINCIPAL
    // =========================
    const matchTexto =
        includes(t.patrimonio) ||
        includes(t.serial) ||
        includes(t.nometelefone) ||
        (Array.isArray(t.ramais) && t.ramais.some(r => includes(r))) ||
        (Array.isArray(t.pessoas) && t.pessoas.some(p => includes(p))) ||
        (Array.isArray(t.funcionais) && t.funcionais.some(f => includes(f))) ||
        (Array.isArray(t.cpfs) && t.cpfs.some(c => includes(c))) ||
        includes(t.secretaria) ||
        includes(t.departamento) ||
        includes(t.endereco) ||
        includes(t.entregue) ||
        includes(t.lugartelefone);

    // =========================
    // FILTROS BOOLEANOS
    // =========================

    const entregueBool = !!t.entregue; // true se existir data, false se null/undefined
    const matchMontado = matchBool(entregueBool, montado);
    const matchPatrimoniado  = matchBool(!!t.patrimoniado, patrimoniado);
    const matchDefeito       = matchBool(!!t.defeito, defeito);

    // =========================
    // RESULTADO FINAL
    // =========================
    return matchTexto && matchMontado && matchPatrimoniado && matchDefeito;
    });

    preencherTabelaTelefones(listaFiltrada);
}

function aplicarFiltrosTelefone() {
    const patrimonioFiltro       = document.getElementById("filtroPatrimonio").value.toLowerCase();
    const serialFiltro           = document.getElementById("filtroSerial").value.toLowerCase();
    const macFiltro              = document.getElementById("filtroMac").value.toLowerCase();
    const modeloFiltro           = document.getElementById("filtroModelo").value.toLowerCase();
    const secretariaFiltro       = document.getElementById("filtroSecretaria").value.toLowerCase();
    const departamentoFiltro     = document.getElementById("filtroDepartamento").value.toLowerCase();
    const enderecoFiltro         = document.getElementById("filtroEndereco").value.toLowerCase();
    const localFiltro            = document.getElementById("filtroLocal").value.toLowerCase();
    const andarFiltro            = document.getElementById("filtroAndar").value.toLowerCase();
    const ramalFiltro            = document.getElementById("filtroRamal").value.toLowerCase();
    const pessoaFiltro           = document.getElementById("filtroPessoa").value.toLowerCase();
    const funcionalFiltro        = document.getElementById("filtroFuncional").value.toLowerCase();
    const cpfFiltro              = document.getElementById("filtroCpf").value.toLowerCase();
    const dataEntregaFiltro      = document.getElementById("filtroDataEntrega").value;
    const ultimaAlteracaoFiltro  = document.getElementById("filtroUltimaAlteracao").value;

    const filtrados = telefones.filter(t => {
        // 🔹 Função null-safe para texto
        const includes = (valor, filtro) =>
            filtro === "" || (valor !== null && valor !== undefined && valor.toString().toLowerCase().includes(filtro));

        // 🔹 Função para datas
        const matchDate = (campo, filtro) => {
            if (!filtro) return true;
            if (!campo) return false;
            return campo.toString().startsWith(filtro);
        };

        // 🔹 Campos que podem ser arrays
        const includesArray = (arr, filtro) => {
            if (!filtro) return true;
            if (!Array.isArray(arr)) return false;
            return arr.some(item => includes(item, filtro));
        };

        // 🔹 Booleanos null-safe
        const matchBool = (campo, filtro) => filtro === "" || (campo !== null && String(campo) === filtro);

        const entregueBool = !!t.entregue;
        const patrimoniadoBool = !!t.patrimoniado;
        const defeitoBool = !!t.defeito;

        return (
            includes(t.patrimonio, patrimonioFiltro) &&
            includes(t.serial, serialFiltro) &&
            includes(t.mac, macFiltro) &&
            includes(t.modelo, modeloFiltro) &&
            includes(t.secretaria, secretariaFiltro) &&
            includes(t.departamento, departamentoFiltro) &&
            includes(t.endereco, enderecoFiltro) &&
            includes(t.lugartelefone || t.local, localFiltro) &&
            includes(t.andar, andarFiltro) &&
            includesArray(t.ramais, ramalFiltro) &&
            includesArray(t.pessoas, pessoaFiltro) &&
            includesArray(t.funcionais, funcionalFiltro) &&
            includesArray(t.cpfs, cpfFiltro) &&
            matchDate(t.entregue, dataEntregaFiltro) &&
            matchDate(t.ultimaAlteracao, ultimaAlteracaoFiltro) &&
            matchBool(entregueBool, document.getElementById("filtroMontado").value) &&
            matchBool(patrimoniadoBool, document.getElementById("filtroPatrimoniado").value) &&
            matchBool(defeitoBool, document.getElementById("filtroDefeito").value)
        );
    });

    preencherTabelaTelefones(filtrados);
    alert('Filtro aplicado com sucesso!')
    // Fechar modal usando apenas Bootstrap
    fecharModais();

}


function entregarTelefone(idtelefone, idpessoa, iddepartamento, idlugartelefone) {

    if (!idpessoa || !iddepartamento || !idlugartelefone) {
        alert("Telefone não possui pessoa ou local vinculado.");
        return;
    }

    if (!confirm("Deseja registrar a entrega deste telefone?")) return;

    fetch("/entregas/entregar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            idtelefone,
            idpessoa,
            iddepartamento,
            idlugartelefone,
            dataentrega: new Date().toISOString().split("T")[0]
        })
    })
    .then(res => res.json())
    .then(result => {
    alert("Telefone entregue com sucesso!");

    if (result.termo_url) {
        window.open(result.termo_url, "_blank");
    }

    carregarTelefones();
})
    .catch(err => {
        console.error(err);
        alert("Erro ao entregar telefone");
    });
}

function getTelefonesSelecionados() {
    return [...document.querySelectorAll(".checkbox-telefone:checked")]
        .map(cb => parseInt(cb.value));
}

async function entregarTelefonesSelecionados() {
    const telefones = getTelefonesSelecionados();

    if (telefones.length === 0) {
        alert("Selecione ao menos um telefone.");
        return;
    }

    if (!confirm(`Deseja entregar ${telefones.length} telefone(s)?`)) {
        return;
    }

    try {
        const response = await fetch("/entregas/entregarSelecionados", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ telefones })
        });

        // ❌ Se der erro no backend (JSON)
        if (!response.ok) {
            const erro = await response.json();
            alert(erro.error || "Erro ao entregar telefones.");
            return;
        }

        // ✅ SUCESSO → vem PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "termo_entrega_telefone.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        window.URL.revokeObjectURL(url);

        alert("Telefones entregues com sucesso!");
        carregarTelefones(); // recarrega a tabela

    } catch (err) {
        console.error(err);
        alert("Erro de comunicação com o servidor.");
    }
}

async function gerarTermoEntrega() {
    const telefones = getTelefonesSelecionados();

    if (telefones.length === 0) {
        alert("Selecione ao menos um telefone.");
        return;
    }

    try {
        const response = await fetch("/termo/gerartermo", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ telefones })
        });

        // ❌ Se der erro no backend (JSON)
        if (!response.ok) {
            const erro = await response.json();
            alert(erro.error || "Erro ao gerar termo.");
            return;
        }

        // ✅ SUCESSO → vem PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "termo_entrega_telefone.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        window.URL.revokeObjectURL(url);

        alert("Termo gerado com sucesso!");
        carregarTelefones(); // recarrega a tabela

    } catch (err) {
        console.error(err);
        alert("Erro de comunicação com o servidor.");
    }
}

 function abrirModalDefeito() {
    const modal = new bootstrap.Modal(document.getElementById('modalDefeito'));
    modal.show();
  }

 async function gerarTermoGarantiaComDefeito() {
    const defeito = document.getElementById('descricaoDefeito').value.trim();
    if(defeito === "") {
      alert("Por favor, descreva o defeito antes de enviar.");
      return;
    }

    fecharModais();
    // Agora chama a função original passando o defeito
    await gerarTermoGarantia(defeito);
  }

  // Função original, agora recebe defeito como parâmetro
  async function gerarTermoGarantia(defeito) {
    const telefones = getTelefonesSelecionados();

    if (telefones.length === 0) {
        alert("Selecione ao menos um telefone.");
        return;
    }

    try {
        const response = await fetch("/garantia/gerartermogarantia", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ telefones, defeito }) // Passa o defeito para o backend
        });

        if (!response.ok) {
            const erro = await response.json();
            alert(erro.error || "Erro ao gerar termo de garantia.");
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "termo_garantia_telefone.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        window.URL.revokeObjectURL(url);

        alert("Termo de garantia gerado com sucesso!");
        carregarTelefones();

    } catch (err) {
        console.error(err);
        alert("Erro de comunicação com o servidor.");
    }
  }


// Escuta eventos
searchInput.addEventListener("input", atualizarTabela);
filtroMontado.addEventListener("change", atualizarTabela);
filtroPatrimoniado.addEventListener("change", atualizarTabela);
filtroDefeito.addEventListener("change", atualizarTabela);


document.addEventListener("DOMContentLoaded", async () => {
    await carregarTodasTelefones();  // Para modais
    carregarTelefones(1);            // Página 1
    carregarDepartamentos();
    carregarSecretarias();
    carregarLugarTelefone();
    carregarModelo();
});


function mostrarLoadingTabela() {
    document.getElementById("loadingTabela").classList.remove("d-none");

    const tabelaTodos = document.getElementById("containerTabelaTodos");
    const tabelaGarantia = document.getElementById("containerTabelaGarantia");

    if (tabelaTodos) tabelaTodos.classList.add("d-none");
    if (tabelaGarantia) tabelaGarantia.classList.add("d-none");
}

function esconderLoadingTabela() {
    document.getElementById("loadingTabela").classList.add("d-none");

    const tabelaTodos = document.getElementById("containerTabelaTodos");
    const tabelaGarantia = document.getElementById("containerTabelaGarantia");

    if (tabelaTodos) tabelaTodos.classList.remove("d-none");
    if (tabelaGarantia) tabelaGarantia.classList.remove("d-none");
}


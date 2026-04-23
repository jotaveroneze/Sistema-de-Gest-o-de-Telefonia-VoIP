const PER_PAGE_RAMAL = 10;

const CONFIG_ABAS = {
    geral: {
        endpoint: '/ramal/listar',
        tabela: 'tabelaRamal',
        anterior: 'btnAnteriorGeral',
        per_page: 12,
        proxima: 'btnProximaGeral',
        retroceder: 'btnRetrocederGeral',
        avancar: 'btnAvancarGeral',
        paginas: 'listaPaginasGeral',
        info: 'infoPaginacaoGeral',
        contador: 'contadorRamais'
    },
    'em-uso': {
        endpoint: '/ramal/listar_em_uso',
        tabela: 'tabelaRamalEmUso',
        anterior: 'btnAnteriorEmUso',
        per_page: 4,
        proxima: 'btnProximaEmUso',
        retroceder: 'btnRetrocederEmUso',
        avancar: 'btnAvancarEmUso',
        paginas: 'listaPaginasEmUso',
        info: 'infoPaginacaoEmUso'
    },
    vago: {
        endpoint: '/ramal/listar_vago',
        tabela: 'tabelaRamalVago',
        anterior: 'btnAnteriorVago',
        per_page: 15,
        proxima: 'btnProximaVago',
        retroceder: 'btnRetrocederVago',
        avancar: 'btnAvancarVago',
        paginas: 'listaPaginasVago',
        info: 'infoPaginacaoVago'
    },
    detalhe: {
        endpoint: '/ramal/listar_detalhe',
        tabela: 'tabelaRamalDetalhe',
        anterior: 'btnAnteriorDetalhe',
        per_page: 1,
        proxima: 'btnProximaDetalhe',
        retroceder: 'btnRetrocederDetalhe',
        avancar: 'btnAvancarDetalhe',
        paginas: 'listaPaginasDetalhe',
        info: 'infoPaginacaoDetalhe'
    }
};

let dadosAbas = {
    geral: { page: 1, dados: [], total: 0, pages: 0 },
    'em-uso': { page: 1, dados: [], total: 0, pages: 0 },
    vago: { page: 1, dados: [], total: 0, pages: 0 },
    detalhe: { page: 1, dados: [], total: 0, pages: 0 }
};

// 🔧 VARIÁVEIS GLOBAIS CORRIGIDAS
let troncoSelecionadaEditarId = null;  // ✅ Corrigido nome

document.addEventListener("DOMContentLoaded", () => {
    // Carrega modais/dropdowns
    if (typeof carregarOperadoras === 'function') carregarOperadoras();
    if (typeof carregarTroncoModal === 'function') carregarTroncoModal();
    if (typeof carregarTroncoEditar === 'function') carregarTroncoEditar();
    if (typeof carregarDepartamentos === 'function') carregarDepartamentos();

    // Carrega aba geral
    carregarAbaAtual();

    // Filtros
    const searchInput = document.getElementById("searchRamal");
    const gravadoSelect = document.getElementById("filtroGravado");
    if (searchInput) searchInput.addEventListener("input", debounce(aplicarFiltros, 300));
    if (gravadoSelect) gravadoSelect.addEventListener("change", aplicarFiltros);

    // Tabs
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', (e) => {
            const targetId = e.target.getAttribute('data-bs-target');
            const abaKey = targetId.replace('#tab-', '');
            carregarAba(abaKey);
        });
    });
});

function debounce(func, wait) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

async function carregarAbaAtual() {
    const activeTab = document.querySelector('.nav-link.active')?.getAttribute('data-bs-target');
    if (activeTab) {
        const abaKey = activeTab.replace('#tab-', '');
        await carregarAba(abaKey);
    }
}

async function carregarAba(abaKey) {
    const config = CONFIG_ABAS[abaKey];
    if (!config) return console.warn('Aba inválida:', abaKey);

    dadosAbas[abaKey].page = 1;
    carregarDadosAba(abaKey, 1);
}

async function carregarDadosAba(abaKey, page = 1) {
    const config = CONFIG_ABAS[abaKey];
    if (!config) return;

    mostrarLoadingTabela();

    try {
        const searchTerm = document.getElementById("searchRamal")?.value?.trim() || '';
        const gravadoFiltro = document.getElementById("filtroGravado")?.value || 'todos';

        const params = new URLSearchParams({
            page: page,
            per_page_RAMAL: config.per_page
        });
        if (searchTerm) params.append('search', searchTerm);
        if (gravadoFiltro !== 'todos') params.append('gravado', gravadoFiltro);

        const response = await fetch(`${config.endpoint}?${params}`);
        if (!response.ok) throw new Error(`Erro ${response.status}`);

        const data = await response.json();
        dadosAbas[abaKey] = {
            dados: data.ramais || data,
            page: data.page || 1,
            total: data.total || 0,
            pages: data.pages || 0,
            has_prev: data.has_prev || false,
            has_next: data.has_next || false
        };

        preencherTabela(abaKey, dadosAbas[abaKey].dados);
        atualizarPaginacao(abaKey);
        if (config.contador) atualizarContador(config.contador, dadosAbas[abaKey]);

    } catch (err) {
        console.error('Erro ao carregar aba:', err);
        document.getElementById(config.tabela).innerHTML = '<tr><td colspan="100%" class="text-center text-danger py-4">Erro ao carregar dados</td></tr>';
    } finally {
        esconderLoadingTabela();
    }
}

function preencherTabela(abaKey, lista) {
    const config = CONFIG_ABAS[abaKey];
    const tabela = document.getElementById(config.tabela);
    if (!tabela) return;

    tabela.innerHTML = lista.length ?
        lista.map(item => criarLinha(abaKey, item)).join('') :
        '<tr><td colspan="100%" class="text-center text-muted py-4">Nenhum registro encontrado</td></tr>';
}

function criarLinha(abaKey, item) {
    switch (abaKey) {
        case 'geral': return criarLinhaGeral(item);
        case 'em-uso': return criarLinhaEmUso(item);
        case 'vago': return criarLinhaVago(item);
        case 'detalhe': return criarLinhaDetalhe(item);
        default: return '<tr><td>Erro</td></tr>';
    }
}

// ✅ FUNÇÕES DE LINHA COMPLETAS
function criarLinhaGeral(item) {
    const emUso = item.em_uso;
    return `
        <tr id="ramal-${item.id}">
            <td>${item.numero || ''}</td>
            <td>${emUso ? '<span class="badge bg-danger">Em uso</span>' : '<span class="badge bg-success">Livre</span>'}</td>
            <td class="text-center">
                ${item.gravado ? '<i class="fa-solid fa-microphone text-success" title="Gravação habilitada"></i>' : '<i class="fa-solid fa-microphone-slash text-danger" title="Gravação desabilitada"></i>'}
            </td>
            <td class="text-center">
                <button class="btn btn-info btn-sm me-1" title="Pessoas" onclick="visualizarPessoasDoRamal(${item.id}, '${item.numero}')" ${!item.id ? 'disabled' : ''}><i class="fa-solid fa-user-group"></i></button>
                <button class="btn btn-secondary btn-sm me-1" title="Visualizar" onclick="visualizarRamal(${item.id}, '${item.numero}')" ${!item.id ? 'disabled' : ''}><i class="fa-solid fa-phone-volume"></i></button>
                <button class="btn btn-warning btn-sm me-1" title="Editar" onclick="abrirEditarRamal(${item.id})" ${!item.id ? 'disabled' : ''}><i class="fa-solid fa-pen"></i></button>
                <button class="btn btn-danger btn-sm ${emUso ? 'disabled' : ''}" title="${emUso ? 'Em uso' : 'Excluir'}" onclick="removerRamal(${item.id})" ${!item.id ? 'disabled' : ''}><i class="fa-solid fa-trash"></i></button>
            </td>
        </tr>`;
}

function criarLinhaVago(item) {
    return `
        <tr id="ramal-${item.id}">
            <td>${item.numero || ''}</td>
            <td class="text-center">${item.gravado ? '<i class="fa-solid fa-microphone text-success"></i>' : '<i class="fa-solid fa-microphone-slash text-danger"></i>'}</td>
            <td>
                <button class="btn btn-info btn-sm me-1" onclick="visualizarPessoasDoRamal(${item.id}, '${item.numero}')"><i class="fa-solid fa-user-group"></i></button>
                <button class="btn btn-secondary btn-sm me-1" onclick="visualizarRamal(${item.id}, '${item.numero}')"><i class="fa-solid fa-phone-volume"></i></button>
                <button class="btn btn-warning btn-sm me-1" onclick="abrirEditarRamal(${item.id})"><i class="fa-solid fa-pen"></i></button>
                <button class="btn btn-danger btn-sm" onclick="removerRamal(${item.id})"><i class="fa-solid fa-trash"></i></button>
            </td>
        </tr>`;
}

function criarLinhaEmUso(item) {
    const telefonesHtml = item.telefones?.map(t => `<div class="mb-1">${t.patrimonio || "-"}</div>`).join('') || '<span class="text-muted">Sem telefone</span>';
    const pessoasHtml = item.telefones?.map(t =>
        t.pessoas?.map(p => `<small>${p.nome || ''} — ${p.secretaria || ''}/${p.departamento || ''}</small>`).join('') || 'Sem pessoas'
    ).join('') || '—';

    return `
        <tr id="ramal-${item.id}">
            <td>${item.numero || ''}</td>
            <td>${telefonesHtml}</td>
            <td>${pessoasHtml}</td>
            <td class="text-center">${item.gravado ? '<i class="fa-solid fa-microphone text-success"></i>' : '<i class="fa-solid fa-microphone-slash text-danger"></i>'}</td>
            <td>
                <button class="btn btn-info btn-sm me-1" onclick="visualizarPessoasDoRamal(${item.id}, '${item.numero}')"><i class="fa-solid fa-user-group"></i></button>
                <button class="btn btn-secondary btn-sm me-1" onclick="visualizarRamal(${item.id}, '${item.numero}')"><i class="fa-solid fa-phone-volume"></i></button>
                <button class="btn btn-warning btn-sm" onclick="abrirEditarRamal(${item.id})"><i class="fa-solid fa-pen"></i></button>
            </td>
        </tr>`;
}

function criarLinhaDetalhe(item) {
    const emUso = item.em_uso;
    const numerosGrupo = item.numeros_grupo?.map(g => `<span class="badge bg-primary me-1">${g.numero}</span>`).join('') || '';
    const telefonesHtml = item.telefones?.map(t => `<div class="mb-1">${t.patrimonio || "-"}</div>`).join('') || 'Sem telefone';
    const pessoasHtml = item.telefones?.map(t =>
        t.pessoas?.map(p => `<small>${p.nome} — ${p.secretaria}/${p.departamento}</small>`).join('')
    ).join('') || '—';

    return `
        <tr id="ramal-${item.id}">
            <td>${item.numero || ''}</td>
            <td class="text-center">${item.gravado ? '<i class="fa-solid fa-microphone text-success"></i>' : '<i class="fa-solid fa-microphone-slash text-danger"></i>'}</td>
            <td>${item.numerochave || ''}</td>
            <td>${item.ramalinicial || ''}</td>
            <td>${item.ramalfinal || ''}</td>
            <td>${item.operadora || ''}</td>
            <td>${item.grupo_captura || ''}</td>
            <td>${emUso ? '<span class="badge bg-danger">Em uso</span>' : '<span class="badge bg-success">Livre</span>'}</td>
            <td>${telefonesHtml}</td>
            <td>${pessoasHtml}</td>
            <td>
                <button class="btn btn-info btn-sm me-1" onclick="visualizarPessoasDoRamal(${item.id}, '${item.numero}')"><i class="fa-solid fa-user-group"></i></button>
                <button class="btn btn-secondary btn-sm me-1" onclick="visualizarRamal(${item.id}, '${item.numero}')"><i class="fa-solid fa-phone-volume"></i></button>
                <button class="btn btn-warning btn-sm me-1" onclick="abrirEditarRamal(${item.id})"><i class="fa-solid fa-pen"></i></button>
                <button class="btn btn-danger btn-sm ${emUso ? 'disabled' : ''}" onclick="removerRamal(${item.id})"><i class="fa-solid fa-trash"></i></button>
            </td>
        </tr>`;
}

// 🔧 RESTO DO CÓDIGO (paginacao, filtros, etc.)
function aplicarFiltros() {
    const activeTab = document.querySelector('.nav-link.active')?.getAttribute('data-bs-target');
    const abaKey = activeTab ? activeTab.replace('#tab-', '') : 'geral';
    dadosAbas[abaKey].page = 1;
    carregarDadosAba(abaKey, 1);
}

function atualizarPaginacao(abaKey) {
    const config = CONFIG_ABAS[abaKey];
    const dados = dadosAbas[abaKey];

    // Botões
    const btnAnt = document.getElementById(config.anterior);
    const btnProx = document.getElementById(config.proxima);
    if (btnAnt) btnAnt.disabled = !dados.has_prev;
    if (btnProx) btnProx.disabled = !dados.has_next;

    // Info
    const infoEl = document.getElementById(config.info);
    if (infoEl) infoEl.textContent = `Página ${dados.page} de ${dados.pages} (${dados.total} total)`;

    // Paginação numérica
    const ul = document.getElementById(config.paginas);
    if (!ul) return;
    ul.innerHTML = '';

    const maxVisible = 5;
    let startPage = Math.max(1, dados.page - 2);
    let endPage = Math.min(dados.pages, startPage + maxVisible - 1);
    if (endPage - startPage + 1 < maxVisible) startPage = Math.max(1, endPage - maxVisible + 1);

    // Botões +/-10
    if (dados.page > 10) {
        const li = document.createElement('li');
        li.className = 'page-item';
        li.innerHTML = `<button class="page-link" onclick="irPagina('${abaKey}', ${Math.max(1, dados.page - 10)})">‹‹</button>`;
        ul.appendChild(li);
    }

    // Páginas
    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === dados.page ? 'active' : ''}`;
        li.innerHTML = `<button class="page-link" onclick="irPagina('${abaKey}', ${i})">${i}</button>`;
        ul.appendChild(li);
    }

    if (dados.page < dados.pages - 10) {
        const li = document.createElement('li');
        li.className = 'page-item';
        li.innerHTML = `<button class="page-link" onclick="irPagina('${abaKey}', ${Math.min(dados.pages, dados.page + 10)})">››</button>`;
        ul.appendChild(li);
    }
}

function irPagina(abaKey, page) {
    dadosAbas[abaKey].page = page;
    carregarDadosAba(abaKey, page);
}

function atualizarContador(elementId, dados) {
    const el = document.getElementById(elementId);
    if (el) el.textContent = `${dados.total} registros`;
}

function mostrarLoadingTabela() {
    const loading = document.getElementById("loadingTabela");
    if (loading) loading.classList.remove("d-none");
}

function esconderLoadingTabela() {
    const loading = document.getElementById("loadingTabela");
    if (loading) loading.classList.add("d-none");
}

// ✅ FUNÇÕES DE EDIÇÃO CORRIGIDAS
async function salvarEdicaoRamal() {
    const id = document.getElementById("editIdRamal")?.value;
    const numero = document.getElementById("txtEditRamal")?.value?.trim();
    const gravado = document.getElementById("editGravado")?.checked || false;
    const idtronco = troncoSelecionadaEditarId;  // ✅ Nome corrigido

    if (!numero || !id || !idtronco) {
        alert("Preencha todos os campos!");
        return;
    }

    try {
        const resp = await fetch(`/ramal/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ numero, idtronco, gravado: gravado ? 1 : 0 })
        });

        const data = await resp.json();
        if (!resp.ok) throw new Error(data.erro || "Erro ao editar");

        alert("Ramal atualizado com sucesso!");

        // Recarrega aba atual
        const activeTab = document.querySelector('.nav-link.active')?.getAttribute('data-bs-target');
        const abaKey = activeTab ? activeTab.replace('#tab-', '') : 'geral';
        carregarDadosAba(abaKey, dadosAbas[abaKey].page);

    } catch (e) {
        console.error(e);
        alert("Erro ao editar ramal: " + e.message);
    }
}

function abrirEditarRamal(id) {
    // Busca nos dados da aba atual
    const activeTab = document.querySelector('.nav-link.active')?.getAttribute('data-bs-target');
    const abaKey = activeTab ? activeTab.replace('#tab-', '') : 'geral';

    const item = dadosAbas[abaKey].dados.find(r => r.id == id);
    if (!item) {
        alert("Ramal não encontrado!");
        return;
    }

    document.getElementById("editIdRamal").value = item.id;
    document.getElementById("txtEditRamal").value = item.numero || '';
    document.getElementById("editGravado").checked = item.gravado == 1 || item.gravado === true;

    troncoSelecionadaEditarId = item.idtronco || null;
    if (typeof carregarTroncoEditar === 'function') carregarTroncoEditar();

    new bootstrap.Modal(document.getElementById("modalEditarRamal")).show();
}


function filtrarRamais(tipo) {

    // ativa aba clicada
    document.querySelectorAll("#ramalTabs .nav-link").forEach(tab => {
        tab.classList.remove("active");
    });
    event.target.classList.add("active");

    let filtrados = ramal;

    switch (tipo) {
        case "geral":
            filtrados = ramais.filter(r => r.em_uso === true);
            break;

        case "em_uso":
            filtrados = ramais.filter(r => r.gravado === true);
            break;

        case "vago":
            filtrados = ramais.filter(r => r.gravado === false);
            break;

        case "detalhe":
            filtrados = ramais.filter(r => r.status === 0);
            break;

    }

    preencherTabelaRamal(filtrados);
}

function esconderLoadingTabela() {
    document.getElementById("loadingTabela").classList.add("d-none");

    const tabelaGeral = document.getElementById("containerTabelaGeral");
    const tabelaRamalEmUso = document.getElementById("containerTabelaEmUso");
    const tabelaRamalVago = document.getElementById("containerTabelaVago");
    const tabelaRamalDetalhe = document.getElementById("containerTabelaDetalhe");

    if (tabelaGeral) tabelaGeral.classList.remove("d-none");
    if (tabelaRamalEmUso) tabelaRamalEmUso.classList.remove("d-none");
    if (tabelaRamalVago) tabelaRamalVago.classList.remove("d-none");
    if (tabelaRamalDetalhe) tabelaRamalDetalhe.classList.remove("d-none");
}

//#endregion

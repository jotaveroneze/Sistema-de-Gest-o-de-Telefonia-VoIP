const CONFIG_ABAS = {
    pendentes: {
        endpoint: '/pendencias/listar',
        tabela: 'tabelaPendentes',
        anterior: 'btnAnteriorPendentes',
        per_page: 10,
        proxima: 'btnProximaPendentes',
        retroceder: 'btnRetrocederPendentes',
        avancar: 'btnAvancarPendentes',
        paginas: 'listaPaginasPendentes',
        info: 'infoPaginacaoPendentes',
        contador: 'contadorPendentes'
    },
    finalizadas: {
        endpoint: '/pendencias/listarfinalizadas',
        tabela: 'tabelaFinalizados',  // ✅ Corrigido do HTML
        anterior: 'btnAnteriorFinalizadas',
        per_page: 10,
        proxima: 'btnProximaFinalizadas',
        retroceder: 'btnRetrocederFinalizadas',
        avancar: 'btnAvancarFinalizadas',
        paginas: 'listaPaginasFinalizadas',
        info: 'infoPaginacaoFinalizadas',
        contador: null  // Não tem no HTML finalizadas
    }
};

let dadosAbas = {
    pendentes: { page: 1, dados: [], total: 0, pages: 0, has_prev: false, has_next: false },
    finalizadas: { page: 1, dados: [], total: 0, pages: 0, has_prev: false, has_next: false }
};

let searchTerm = '';
let filtroTipo = '';

// 🔸 UTILITÁRIOS
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatarData(data) {
    if (!data) return "-";
    const d = new Date(data);
    return d.toLocaleDateString("pt-BR");
}

function iconeTipoPendencia(tipo) {
    switch (Number(tipo)) {
        case 1: return `<i class="bi bi-question-circle" title="Outros"></i>`;
        case 2: case 22: return `<i class="bi bi-telephone" title="Mudança de ramal"></i>`;
        case 3: case 32: return `<i class="bi bi-diagram-3" title="Número virtual"></i>`;
        case 4: case 42: return `<i class="bi bi-person-lines-fill" title="Pessoa telefone"></i>`;
        case 5: return `<i class="bi bi-people" title="Grupo captura"></i>`;
        default: return `-`;
    }
}

function getAbaAtiva() {
    const activeTab = document.querySelector('.nav-link.active');
    if (activeTab) return activeTab.getAttribute('data-bs-target')?.replace('#tab-', '') || 'pendentes';

    const activePanel = document.querySelector('.tab-pane.active');
    if (activePanel) return activePanel.id?.replace('tab-', '') || 'pendentes';

    return 'pendentes';
}

// 🔸 PAGINAÇÃO
function atualizarPaginacao(config, dados, abaKey) {
    // Info
    const infoEl = document.getElementById(config.info);
    if (infoEl) {
        const inicio = (dados.page - 1) * config.per_page + 1;
        const fim = Math.min(dados.page * config.per_page, dados.total);
        infoEl.textContent = `Mostrando ${inicio}-${fim} de ${dados.total}`;
    }

    // Contador (só pendentes)
    const contadorEl = document.getElementById(config.contador);
    if (contadorEl) contadorEl.textContent = `${dados.total} registros`;

    // Botões
    const btnAnterior = document.getElementById(config.anterior);
    const btnProxima = document.getElementById(config.proxima);
    const btnRetroceder = document.getElementById(config.retroceder);
    const btnAvancar = document.getElementById(config.avancar);

    if (btnAnterior) btnAnterior.disabled = !dados.has_prev;
    if (btnProxima) btnProxima.disabled = !dados.has_next;
    if (btnRetroceder) btnRetroceder.disabled = !dados.has_prev;
    if (btnAvancar) btnAvancar.disabled = !dados.has_next;

    // Páginas numeradas
    const paginasEl = document.getElementById(config.paginas);
    if (paginasEl && dados.pages > 1) {
        paginasEl.innerHTML = '';
        const maxVisible = 5;
        let startPage = Math.max(1, dados.page - Math.floor(maxVisible / 2));
        let endPage = Math.min(dados.pages, startPage + maxVisible - 1);
        if (endPage - startPage + 1 < maxVisible) startPage = Math.max(1, endPage - maxVisible + 1);

        if (startPage > 1) {
            paginasEl.innerHTML += `<button class="btn btn-sm btn-outline-secondary me-1" onclick="irPagina('${abaKey}', 1)">1</button>`;
            if (startPage > 2) paginasEl.innerHTML += `<span class="mx-1">...</span>`;
        }

        for (let i = startPage; i <= endPage; i++) {
            paginasEl.innerHTML += `<button class="btn btn-sm ${i === dados.page ? 'btn-primary' : 'btn-outline-secondary'} me-1" onclick="irPagina('${abaKey}', ${i})">${i}</button>`;
        }

        if (endPage < dados.pages) {
            if (endPage < dados.pages - 1) paginasEl.innerHTML += `<span class="mx-1">...</span>`;
            paginasEl.innerHTML += `<button class="btn btn-sm btn-outline-secondary" onclick="irPagina('${abaKey}', ${dados.pages})">${dados.pages}</button>`;
        }
    } else if (paginasEl) {
        paginasEl.innerHTML = '';
    }
}

// 🔸 TABELAS
function preencherTabela(tabelaId, lista, isFinalizadas = false) {
    const tbody = document.querySelector(`#${tabelaId}`);
    if (!tbody) return;

    if (lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="' + (isFinalizadas ? '6' : '4') + '" class="text-center text-muted py-4">Nenhuma pendência encontrada</td></tr>';
        return;
    }

    tbody.innerHTML = lista.map(p => {
        const icon = iconeTipoPendencia(p.tipopendencia);

        if (!isFinalizadas) {
            return `
                <tr id="pendencia-${p.id}">
                    <td class="text-center">${icon}</td>
                    <td>${p.descricaotipendencia ?? "-"}</td>
                    <td>${formatarData(p.dataentrada)}</td>
                    <td>
                        <div class="btn-group btn-group-sm" role="group">
                            <button class="btn btn-success" onclick="finalizarPendencia(${p.id})" title="Finalizar">
                                <i class="fa-solid fa-check"></i>
                            </button>
                            <button class="btn btn-danger" onclick="removerPendencia(${p.id})" title="Excluir">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>`;
        } else {
            return `
                <tr id="pendencia-${p.id}">
                    <td class="text-center">${icon}</td>
                    <td>${p.descricaotipendencia ?? "-"}</td>
                    <td>${formatarData(p.dataentrada)}</td>
                    <td>${formatarData(p.datasaida)}</td>
                    <td>${p.usuarioresolvido ?? "-"}</td>
                    <td>
                        <div class="btn-group btn-group-sm" role="group">
                            <button class="btn btn-primary" onclick="devolverPendencia(${p.id})" title="Devolver">
                                <i class="fa-solid fa-rotate-left"></i>
                            </button>
                            <button class="btn btn-danger" onclick="removerPendencia(${p.id})" title="Excluir">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>`;
        }
    }).join('');
}

// 🔸 CARREGAMENTO
async function carregarDadosAba(abaKey) {
    const config = CONFIG_ABAS[abaKey];
    if (!config) return console.error('❌ Config não encontrada:', abaKey);

    const tbody = document.querySelector(`#${config.tabela}`);
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="' + (abaKey === 'finalizadas' ? '6' : '4') + '" class="text-center p-4"><div class="spinner-border text-primary" role="status"></div></td></tr>';
    }

    const params = new URLSearchParams({
        page: dadosAbas[abaKey].page,
        per_page: config.per_page,
        search: searchTerm,
        filtro_tipo: filtroTipo
    });

    console.log('📡 GET:', `${config.endpoint}?${params}`);

    try {
        const response = await fetch(`${config.endpoint}?${params}`);
        console.log('📊 Status:', response.status);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        console.log('✅ Data:', data);

        dadosAbas[abaKey] = {
            page: data.page || 1,
            dados: data.pendencias || [],
            total: data.total || 0,
            pages: data.pages || 0,
            has_prev: data.has_prev || false,
            has_next: data.has_next || false
        };

        preencherTabela(config.tabela, dadosAbas[abaKey].dados, abaKey === 'finalizadas');
        atualizarPaginacao(config, dadosAbas[abaKey], abaKey);

    } catch (err) {
        console.error('❌ Erro:', err);
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="${abaKey === 'finalizadas' ? '6' : '4'}" class="text-center text-danger p-4">❌ ${err.message}</td></tr>`;
        }
    }
}

// 🔸 NAVEGAÇÃO
async function irPagina(abaKey, page) {
    dadosAbas[abaKey].page = page;
    await carregarDadosAba(abaKey);
}

window.proximaPagina = async function(abaKey, direcao) {
    const dados = dadosAbas[abaKey];
    if (direcao === -1 && !dados.has_prev) return;
    if (direcao === 1 && !dados.has_next) return;
    dados.page += direcao;
    await carregarDadosAba(abaKey);
};

async function carregarAbaAtual() {
    const abaAtiva = getAbaAtiva();
    dadosAbas[abaAtiva].page = 1;
    await carregarDadosAba(abaAtiva);
}

async function aplicarFiltros() {
    searchTerm = document.getElementById("searchPendencias")?.value || '';
    filtroTipo = document.getElementById("filtroTipo")?.value || '';
    const abaAtiva = getAbaAtiva();
    dadosAbas[abaAtiva].page = 1;
    await carregarDadosAba(abaAtiva);
}

// 🔸 AÇÕES
async function removerPendencia(id) {
    if (!confirm("Remover esta pendência?")) return;
    try {
        const res = await fetch(`/pendencias/remover/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            alert(data.mensagem);
            carregarAbaAtual();
        } else alert(data.erro || "Erro");
    } catch (e) {
        console.error(e);
        alert("Erro de rede");
    }
}

async function finalizarPendencia(id) {
    if (!confirm("Finalizar esta pendência?")) return;
    try {
        const res = await fetch(`/pendencias/entregar/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            alert(data.mensagem);
            carregarAbaAtual();
        } else alert(data.erro || "Erro");
    } catch (e) {
        alert("Erro de rede");
    }
}

async function devolverPendencia(id) {
    if (!confirm("Devolver esta pendência?")) return;
    try {
        const res = await fetch(`/pendencias/devolver/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            alert(data.mensagem);
            carregarAbaAtual();
        } else alert(data.erro || "Erro");
    } catch (e) {
        alert("Erro de rede");
    }
}

function abrirModalNovaPendencia() {
    const el = document.getElementById('modalNovaPendencia');
    if (!el) return console.error('Modal não encontrado');
    const modal = new bootstrap.Modal(el);
    modal.show();
}

async function criarPendencia() {
    const texto = document.getElementById("textoPendencia").value.trim();
    if (!texto) return alert("Digite a pendência");

    try {
        const response = await fetch(`/pendencias/criar/${encodeURIComponent(texto)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idtelefoneramal: null, idpessoatelefone: null, idramalnumerogrupo: null })
        });
        const dados = await response.json();
        if (!response.ok) return alert(dados.erro || "Erro");
        alert(dados.mensagem);
        document.getElementById("textoPendencia").value = "";
        carregarAbaAtual();
    } catch (erro) {
        alert("Erro de servidor");
    }
}

// 🔸 INICIALIZAÇÃO ÚNICA
document.addEventListener("DOMContentLoaded", async () => {
    console.log('🚀 Pendências carregando...');

    // Carrega aba pendentes por padrão
    await carregarDadosAba('pendentes');

    // Eventos
    document.getElementById("searchPendencias")?.addEventListener("input", debounce(aplicarFiltros, 300));
    document.getElementById("filtroTipo")?.addEventListener("change", aplicarFiltros);

    // Tabs
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', async (e) => {
            const abaKey = e.target.getAttribute('data-bs-target')?.replace('#tab-', '');
            if (abaKey && CONFIG_ABAS[abaKey]) {
                console.log('🔄 Tab:', abaKey);
                dadosAbas[abaKey].page = 1;
                await carregarDadosAba(abaKey);
            }
        });
    });

    console.log('✅ Pronto!');
});
// 🔧 TODOS BOTÕES (ÚNICO DOMContentLoaded)
document.addEventListener('DOMContentLoaded', function () {
    const botoes = {
        btnAnteriorPendentes:    () => window.proximaPagina('pendentes', -1),
        btnProximaPendentes:     () => window.proximaPagina('pendentes', 1),
        btnRetrocederPendentes:  () => pularPaginas('pendentes', -10),
        btnAvancarPendentes:     () => pularPaginas('pendentes', 10),
        btnAnteriorFinalizadas:  () => window.proximaPagina('finalizadas', -1),
        btnProximaFinalizadas:   () => window.proximaPagina('finalizadas', 1),
        btnRetrocederFinalizadas:() => pularPaginas('finalizadas', -10),
        btnAvancarFinalizadas:   () => pularPaginas('finalizadas', 10),
    };

    Object.entries(botoes).forEach(([id, fn]) => {
        const el = document.getElementById(id);
        if (el) el.onclick = fn;
    });

    console.log('✅ Botões inicializados!');
});


// 🔧 FUNÇÃO PULAR (adicione antes)
function pularPaginas(abaKey, passos) {
    const dados = dadosAbas[abaKey];
    dados.page = Math.max(1, Math.min(dados.pages, dados.page + passos));
    carregarDadosAba(abaKey);
}


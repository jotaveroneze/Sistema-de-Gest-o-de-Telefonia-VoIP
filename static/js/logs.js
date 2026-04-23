// 🔸 CONFIG (igual lugartelefone)
const CONFIG_LOGS = {
    listar: {
        endpoint: '/logs/listar',
        tabela: 'tabelaLogs',
        paginas: 'listaPaginasLogs',
        info: 'infoPaginacaoLogs',
        contador: 'contadorLogs',
        per_page: 3
    }
};

let dadosLogs = {
    listar: { page: 1, dados: [], total: 0, pages: 0, has_prev: false, has_next: false }
};

let searchTerm = '';
let filtroData = '';

function formatarData(data) {
    if (!data) return "";
    const novaData = new Date(data);
    return novaData.toLocaleString("pt-BR", {
        day: "2-digit", month: "2-digit", year: "numeric",
        hour: "2-digit", minute: "2-digit", second: "2-digit"
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => { clearTimeout(timeout); func(...args); };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function atualizarPaginacao(config, dados) {
    const infoEl = document.getElementById(config.info);
    if (infoEl) {
        const inicio = (dados.page - 1) * config.per_page + 1;
        const fim = Math.min(dados.page * config.per_page, dados.total);
        infoEl.textContent = `Mostrando ${inicio}-${fim} de ${dados.total}`;
    }

    const contadorEl = document.getElementById(config.contador);
    if (contadorEl) contadorEl.textContent = `${dados.total} registros`;

    // Botões Anterior/Próxima
    const btnAnterior = document.getElementById('btnAnteriorLogs');
    const btnProxima = document.getElementById('btnProximaLogs');
    if (btnAnterior) btnAnterior.disabled = !dados.has_prev;
    if (btnProxima) btnProxima.disabled = !dados.has_next;

    const paginasEl = document.getElementById(config.paginas);
    if (paginasEl && dados.pages > 1) {
        paginasEl.innerHTML = '';
        const maxVisible = 5;
        let startPage = Math.max(1, dados.page - Math.floor(maxVisible / 2));
        let endPage = Math.min(dados.pages, startPage + maxVisible - 1);
        if (endPage - startPage + 1 < maxVisible) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }

        if (startPage > 1) {
            paginasEl.innerHTML += '<li class="page-item"><a class="page-link" href="#" onclick="irPaginaLogs(1)">1</a></li>';
            if (startPage > 2) paginasEl.innerHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }

        for (let i = startPage; i <= endPage; i++) {
            const active = i === dados.page ? 'active' : '';
            paginasEl.innerHTML += `<li class="page-item ${active}"><a class="page-link" href="#" onclick="irPaginaLogs(${i})">${i}</a></li>`;
        }

        if (endPage < dados.pages) {
            if (endPage < dados.pages - 1) paginasEl.innerHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            paginasEl.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="irPaginaLogs(${dados.pages})">${dados.pages}</a></li>`;
        }
    } else if (paginasEl) {
        paginasEl.innerHTML = '';
    }
}

function preencherTabelaLogs(lista) {
    const tabela = document.getElementById("tabelaLogs");
    if (!tabela) return;

    if (lista.length === 0) {
        tabela.innerHTML = '<tr><td colspan="10" class="text-center text-muted py-4">Nenhum log encontrado</td></tr>';
        return;
    }

    let html = '';
    lista.forEach(sis => {
        html += `
            <tr>
                <td>${formatarData(sis.data)}</td>
                <td>${sis.entidade ?? ""}</td>
                <td>${sis.antes ?? ""}</td>
                <td>${sis.depois ?? ""}</td>
                <td>${sis.usuario ?? ""}</td>
                <td>${sis.email ?? ""}</td>
                <td>${sis.ip ?? ""}</td>
                <td>${sis.rota ?? ""}</td>
                <td>${sis.retorno ?? ""}</td>
                <td>${sis.mensagem ?? ""}</td>
            </tr>
        `;
    });
    tabela.innerHTML = html;
}

// 🔸 CARREGAMENTO PRINCIPAL
async function carregarDadosLogs() {
    const config = CONFIG_LOGS.listar;
    const tabela = document.getElementById(config.tabela);
    if (tabela) {
        tabela.innerHTML = '<tr><td colspan="10" class="text-center p-4"><div class="spinner-border text-primary" role="status"></div></td></tr>';
    }

    const params = new URLSearchParams({
        page: dadosLogs?.listar?.page || 1,
        per_page: config.per_page,
        search: searchTerm,
        data: filtroData
    });

    try {
        const response = await fetch(`${config.endpoint}?${params}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // ✅ CORREÇÃO: Trata resposta vazia como dados vazios
        dadosLogs.listar = {
            page: data?.page || 1,
            dados: data?.data || [],  // Sempre garante array
            total: data?.total || 0,
            pages: data?.pages || 0,
            has_prev: data?.has_prev || false,
            has_next: data?.has_next || false
        };

        // ✅ Remove esta validação que causa o erro
        // if (!data) {
        //     throw new Error("API retornou vazio");
        // }

        const logs = dadosLogs.listar.dados;
        preencherTabelaLogs(logs);  // Já trata lista vazia
        atualizarPaginacao(config, dadosLogs.listar);

    } catch (err) {
        console.error('❌ Erro:', err);
        if (tabela) {
            tabela.innerHTML = `<tr><td colspan="10" class="text-center text-danger p-4">❌ ${err.message}</td></tr>`;
        }
    }
}

// 🔸 NAVEGAÇÃO 10 EM 10
async function retroceder10Logs() {
    const novaPagina = Math.max(1, dadosLogs.listar.page - 10);
    dadosLogs.listar.page = novaPagina;
    await carregarDadosLogs();
}

async function avancar10Logs() {
    const maxPagina = dadosLogs.listar.pages || 1;
    const novaPagina = Math.min(maxPagina, dadosLogs.listar.page + 10);
    dadosLogs.listar.page = novaPagina;
    await carregarDadosLogs();
}


// 🔸 NAVEGAÇÃO
async function irPaginaLogs(page) {
    dadosLogs.listar.page = page;
    await carregarDadosLogs();
}

async function aplicarFiltrosLogs() {
    searchTerm = document.getElementById("searchLogs")?.value || '';
    filtroData = document.getElementById("filterDate")?.value || '';
    dadosLogs.listar.page = 1;
    await carregarDadosLogs();
}

// 🔸 INICIALIZAÇÃO
document.addEventListener("DOMContentLoaded", async () => {
    console.log('🚀 Logs carregando...');

    await carregarDadosLogs();

    // Eventos filtros
    document.getElementById("searchLogs")?.addEventListener("input", debounce(aplicarFiltrosLogs, 300));
    document.getElementById("filterDate")?.addEventListener("change", aplicarFiltrosLogs);

    // 🔸 BOTÕES ANTERIOR/PRÓXIMA (já tem)
    document.getElementById('btnAnteriorLogs')?.addEventListener('click', () => {
        if (dadosLogs.listar.has_prev) {
            dadosLogs.listar.page--;
            carregarDadosLogs();
        }
    });

    document.getElementById('btnProximaLogs')?.addEventListener('click', () => {
        if (dadosLogs.listar.has_next) {
            dadosLogs.listar.page++;
            carregarDadosLogs();
        }
    });

    // ✅ NOVOS BOTÕES 10 EM 10 + PRIMEIRA/ÚLTIMA
    document.getElementById('btnRetrocederLogs')?.addEventListener('click', retroceder10Logs);
    document.getElementById('btnAvancarLogs')?.addEventListener('click', avancar10Logs);
    document.getElementById('btnPrimeiraLogs')?.addEventListener('click', () => irPaginaLogs(1));
    document.getElementById('btnUltimaLogs')?.addEventListener('click', () => irPaginaLogs(dadosLogs.listar.pages || 1));

    console.log('✅ Logs pronto!');
});

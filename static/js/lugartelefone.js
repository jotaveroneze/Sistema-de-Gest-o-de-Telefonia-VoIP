const CONFIG_LUGARTELEFONE = {
    listar: {
        endpoint: '/lugartelefone/listar',
        tabela: 'tabelaLugarTelefone',
        paginas: 'listaPaginasLugar',           // ← Era paginacaoLugarTelefone
        info: 'infoPaginacaoLugar',             // ← Era infoPaginacaoLugarTelefone
        contador: 'contadorLugares',
        per_page: 10
    }
};


let dadosLugarTelefone = {
    listar: { page: 1, dados: [], total: 0, pages: 0, has_prev: false, has_next: false }
};
let searchTerm = '';
let filtroAndar = '';

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

// 🔸 BOTÕES ANTERIOR/PRÓXIMA (igual pendencias)
function atualizarBotoesNavegacao(dados) {
    const btnAnterior = document.getElementById('btnAnteriorLugar');
    const btnProxima = document.getElementById('btnProximaLugar');
    const btnRetroceder = document.getElementById('btnRetrocederLugar');
    const btnAvancar = document.getElementById('btnAvancarLugar');

    if (btnAnterior) btnAnterior.disabled = !dados.has_prev;
    if (btnProxima) btnProxima.disabled = !dados.has_next;
    if (btnRetroceder) btnRetroceder.disabled = dados.page <= 1;
    if (btnAvancar) btnAvancar.disabled = dados.page >= dados.pages;
}

// 🔸 EVENTOS DOS BOTÕES
function adicionarEventosBotoes() {
    // Anterior
    document.getElementById('btnAnteriorLugar')?.addEventListener('click', () => {
        if (dadosLugarTelefone.listar.has_prev) {
            dadosLugarTelefone.listar.page--;
            carregarDadosLugarTelefone();
        }
    });

    // Próxima
    document.getElementById('btnProximaLugar')?.addEventListener('click', () => {
        if (dadosLugarTelefone.listar.has_next) {
            dadosLugarTelefone.listar.page++;
            carregarDadosLugarTelefone();
        }
    });

    // Retroceder 10 páginas
    document.getElementById('btnRetrocederLugar')?.addEventListener('click', () => {
        dadosLugarTelefone.listar.page = Math.max(1, dadosLugarTelefone.listar.page - 10);
        carregarDadosLugarTelefone();
    });

    // Avançar 10 páginas
    document.getElementById('btnAvancarLugar')?.addEventListener('click', () => {
        dadosLugarTelefone.listar.page = Math.min(
            dadosLugarTelefone.listar.pages,
            dadosLugarTelefone.listar.page + 10
        );
        carregarDadosLugarTelefone();
    });
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
            paginasEl.innerHTML += '<button class="btn btn-sm btn-outline-secondary me-1" onclick="irPaginaLugarTelefone(1)">1</button>';
            if (startPage > 2) paginasEl.innerHTML += '<span class="mx-1">...</span>';
        }

        for (let i = startPage; i <= endPage; i++) {
            const classe = i === dados.page ? 'btn-primary' : 'btn-outline-secondary';
            paginasEl.innerHTML += `<button class="btn btn-sm ${classe} me-1" onclick="irPaginaLugarTelefone(${i})">${i}</button>`;
        }

        if (endPage < dados.pages) {
            if (endPage < dados.pages - 1) paginasEl.innerHTML += '<span class="mx-1">...</span>';
            paginasEl.innerHTML += `<button class="btn btn-sm btn-outline-secondary" onclick="irPaginaLugarTelefone(${dados.pages})">${dados.pages}</button>`;
        }
    } else if (paginasEl) {
        paginasEl.innerHTML = '';
    }

    // 🔸 NOVO: CONTROLE DOS BOTÕES ANTERIOR/PRÓXIMA
    const btnAnterior = document.getElementById('btnAnteriorLugar');
    const btnProxima = document.getElementById('btnProximaLugar');
    const btnRetroceder = document.getElementById('btnRetrocederLugar');
    const btnAvancar = document.getElementById('btnAvancarLugar');

    if (btnAnterior) btnAnterior.disabled = !dados.has_prev;
    if (btnProxima) btnProxima.disabled = !dados.has_next;
    if (btnRetroceder) btnRetroceder.disabled = dados.page <= 1;
    if (btnAvancar) btnAvancar.disabled = dados.page >= dados.pages;
}


function preencherTabela(tabelaId, lista) {
    const tbody = document.querySelector('#' + tabelaId);
    if (!tbody) return;

    if (lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">Nenhum lugar telefone encontrado</td></tr>';
        return;
    }

    let html = '';
    lista.forEach(sis => {
        html += `
            <tr id="lugar-${sis.id}">
                <td>${sis.nomelugar || '-'}</td>
                <td>${sis.endereco || '-'}</td>
                <td>${sis.secretaria || '-'}</td>
                <td>${sis.departamento || '-'}</td>
                <td>${sis.andar || '-'}</td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-warning" onclick="abrirEditarLugartelefone(${sis.id})" title="Editar">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="btn btn-danger" onclick="removerLugartelefone(${sis.id})" title="Excluir">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

async function carregarDadosLugarTelefone() {
    const config = CONFIG_LUGARTELEFONE.listar;
    const tbody = document.querySelector('#' + config.tabela);
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center p-4"><div class="spinner-border text-primary" role="status"></div></td></tr>';
    }

    const params = new URLSearchParams({
        page: dadosLugarTelefone.listar.page,
        per_page: config.per_page,
        search: searchTerm,
        andar: filtroAndar
    });

    console.log('🔍 URL:', config.endpoint + '?' + params); // DEBUG 1
    console.log('🔍 PAGE atual:', dadosLugarTelefone.listar.page); // DEBUG 2

    try {
        const response = await fetch(config.endpoint + '?' + params);
        console.log('🔍 Response OK:', response.ok); // DEBUG 3
        console.log('🔍 Status:', response.status); // DEBUG 4

        if (!response.ok) throw new Error('HTTP ' + response.status);

        const data = await response.json();
        console.log('🔍 DATA COMPLETA:', data); // DEBUG 5 - O MAIS IMPORTANTE
        console.log('🔍 DATA.data:', data.data); // DEBUG 6
        console.log('🔍 DATA.pages:', data.pages); // DEBUG 7

        // Verifica se tem dados
        if (!data || !data.data) {
            console.error('❌ Backend não retornou estrutura esperada!');
            return;
        }

        dadosLugarTelefone.listar = {
            page: data.page || 1,
            dados: data.data || [],
            total: data.total || 0,
            pages: data.pages || 0,
            has_prev: data.has_prev || false,
            has_next: data.has_next || false
        };

        console.log('🔍 dadosLugarTelefone atualizado:', dadosLugarTelefone.listar); // DEBUG 8

        lugartelefones = dadosLugarTelefone.listar.dados;
        preencherTabela(config.tabela, lugartelefones);
        preencherSelectAndares(lugartelefones);
        atualizarPaginacao(config, dadosLugarTelefone.listar);

    } catch (err) {
        console.error('❌ ERRO COMPLETO:', err);
    }
}


async function irPaginaLugarTelefone(page) {
    dadosLugarTelefone.listar.page = page;
    await carregarDadosLugarTelefone();
}

async function aplicarFiltrosLugarTelefone() {
    searchTerm = document.getElementById("searchLugartelefone")?.value || '';
    filtroAndar = document.getElementById("selectAndar")?.value || '';
    dadosLugarTelefone.listar.page = 1;
    await carregarDadosLugarTelefone();
}

async function removerLugartelefone(id) {
    if (!confirm("Remover este lugar?")) return;

    try {
        const res = await fetch('/lugartelefone/remover/' + id, { method: 'DELETE' });
        const data = await res.json();

        if (res.ok) {
            alert(data.mensagem || "Lugar removido");
            carregarDadosLugarTelefone();
        } else {
            alert(data.erro || "Erro");
        }
    } catch (e) {
        console.error(e);
        alert("Erro de rede");
    }
}

async function abrirEditarLugartelefone(id) {
    try {
        const response = await fetch('/lugartelefone/' + id);
        if (!response.ok) throw new Error("Erro ao buscar lugar telefone");

        lugarTelefoneEditarId = id;
        const lugar = await response.json();

        document.getElementById("txtEditarNomeLugarTelefone").value = lugar.nomelugar || '';
        document.getElementById("txtEditarEnderecoLugarTelefone").value = lugar.endereco || '';
        document.getElementById("txtEditarAndarLugarTelefone").value = lugar.andar || '';

        if (typeof carregarDepartamentosEditar === "function") {
            await carregarDepartamentosEditar(lugar.iddepartamento);
        }

        const modal = new bootstrap.Modal(document.getElementById("modalEditarLugarTelefone"));
        modal.show();
    } catch (err) {
        console.error(err);
        alert("Erro ao abrir edição do lugar telefone");
    }
}

function preencherSelectAndares(lista) {
    const select = document.getElementById("selectAndar");
    if (!select) return;

    select.innerHTML = '<option value="">Todos os andares</option>';
    const andaresUnicos = [...new Set(lista.map(l => l.andar).filter(a => a))].sort();
    andaresUnicos.forEach(andar => {
        const option = document.createElement("option");
        option.value = andar;
        option.textContent = andar;
        select.appendChild(option);
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    console.log('🚀 LugarTelefone carregando...');

    await carregarDadosLugarTelefone();

    // 🔸 EVENTOS DOS BOTÕES
    document.getElementById('btnAnteriorLugar')?.addEventListener('click', () => {
        if (dadosLugarTelefone.listar.has_prev) {
            dadosLugarTelefone.listar.page--;
            carregarDadosLugarTelefone();
        }
    });

    document.getElementById('btnProximaLugar')?.addEventListener('click', () => {
        if (dadosLugarTelefone.listar.has_next) {
            dadosLugarTelefone.listar.page++;
            carregarDadosLugarTelefone();
        }
    });

    document.getElementById('btnRetrocederLugar')?.addEventListener('click', () => {
        dadosLugarTelefone.listar.page = Math.max(1, dadosLugarTelefone.listar.page - 10);
        carregarDadosLugarTelefone();
    });

    document.getElementById('btnAvancarLugar')?.addEventListener('click', () => {
        dadosLugarTelefone.listar.page = Math.min(
            dadosLugarTelefone.listar.pages,
            dadosLugarTelefone.listar.page + 10
        );
        carregarDadosLugarTelefone();
    });

    // resto dos eventos...
    document.getElementById("searchLugartelefone")?.addEventListener("input", debounce(aplicarFiltrosLugarTelefone, 300));
    document.getElementById("selectAndar")?.addEventListener("change", aplicarFiltrosLugarTelefone);
});


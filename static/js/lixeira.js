/* =========================================================
   FORMATAR DATA
========================================================= */
function formatarData(data) {

    if (!data) return "";

    const novaData = new Date(data);

    return novaData.toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
}


/* =========================================================
   DEFINIR ÍCONE DO TIPO
========================================================= */
function iconeTipoPendencia(tipo) {

    switch (Number(tipo)) {

        case 1:
            return `<i class="bi bi-question-circle" title="Outros"></i>`;

        case 2:
        case 22:
            return `<i class="bi bi-telephone" title="Mudança de ramal"></i>`;

        case 3:
        case 32:
            return `<i class="bi bi-diagram-3" title="Mudança de número/grupo"></i>`;

        case 4:
        case 42:
            return `<i class="bi bi-person-lines-fill" title="Mudança de pessoa"></i>`;

        case 5:
            return `<i class="bi bi-people" title="Grupo de captura"></i>`;

        default:
            return "-";
    }
}


/* =========================================================
   AO CARREGAR A PÁGINA
========================================================= */
document.addEventListener("DOMContentLoaded", () => {

    carregarLixeira();

    const searchInput = document.getElementById("searchLixeira");
    const dateInput = document.getElementById("filterDate");

    if (searchInput)
        searchInput.addEventListener("input", filtrarLixeira);

    if (dateInput)
        dateInput.addEventListener("change", filtrarLixeira);
});


/* =========================================================
   BUSCAR DADOS DA LIXEIRA
========================================================= */
async function carregarLixeira() {

    try {

        const response = await fetch("/lixeira/listar", {
            credentials: "include"
        });

        if (!response.ok)
            throw new Error("Erro ao buscar lixeira");

        const dados = await response.json();

        lixeira = dados;

        preencherTabelaLixeira(lixeira);

    } catch (erro) {

        console.error("Erro:", erro);
        alert("Erro ao carregar lixeira");

    }
}


/* =========================================================
   PREENCHER TABELA
========================================================= */
function preencherTabelaLixeira(lista) {

    const tabela = document.getElementById("tabelaLixeira");

    if (!tabela) return;

    let html = "";

    lista.forEach(p => {

        html += `
            <tr>
                <td class="text-center">
                    ${iconeTipoPendencia(p.tipopendencia)}
                </td>
                <td>${p.descricaotipopendencia ?? ""}</td>
                <td>${formatarData(p.dataentrada)}</td>
                <td>${formatarData(p.datasaida)}</td>
                <td class="text-center">

                    <button class="btn btn-success btn-sm me-2"
                        onclick="restaurarPendencia(${p.id})"
                        title="Restaurar">
                        <i class="bi bi-arrow-counterclockwise"></i>
                    </button>

                    <button class="btn btn-danger btn-sm"
                        onclick="excluirDefinitivo(${p.id})"
                        title="Excluir definitivamente">
                        <i class="fa-solid fa-trash"></i>
                    </button>

                </td>
            </tr>
        `;
    });

    tabela.innerHTML = html;
}


/* =========================================================
   RESTAURAR
========================================================= */
async function restaurarPendencia(id) {

    if(!confirm("Deseja restaurar este registro?"))
        return;

    try {

        const response = await fetch(`/lixeira/restaurar/${id}`, {
            method: "PUT"
        });

        const data = await response.json();

        if (!response.ok)
            throw new Error(data.erro || "Erro ao restaurar");

        alert(data.mensagem);

        carregarLixeira();

    } catch (error) {

        console.error(error);
        alert(error.message);

    }
}


/* =========================================================
   EXCLUIR DEFINITIVO
========================================================= */
async function excluirDefinitivo(id) {

    if (!confirm("Deseja excluir definitivamente este registro?"))
        return;

    try {

        const response = await fetch(`/lixeira/excluir/${id}`, {
            method: "PUT"
        });

        if (!response.ok)
            throw new Error("Erro ao excluir");

        const data = await response.json();

        alert(data.mensagem);

        carregarLixeira();

    } catch (error) {

        console.error(error);
        alert("Erro ao excluir definitivamente.");

    }
}

/* =========================================================
   FILTRO UNIFICADO (TEXTO + DATA + TIPO)
========================================================= */
function filtrarLixeira() {

    if (!lixeira || !lixeira.length) return;

    const filtroTexto =
        document.getElementById("searchLixeira")?.value.toLowerCase().trim() || "";

    const filtroData =
        document.getElementById("filterDate")?.value || ""; // formato: "YYYY-MM-DD"

    // ✅ ID corrigido: era "filtroTipoLixeira" em um lugar e "filtroTipo" em outro
    const filtroTipo =
        document.getElementById("filtroTipo")?.value || "";

    const filtrados = lixeira.filter(item => {

        const descricao = (item.descricaotipopendencia || "").toLowerCase();
        const tipo = Number(item.tipopendencia);

        /* ── FILTRO TEXTO ── */
        const matchTexto =
            !filtroTexto ||
            descricao.includes(filtroTexto) ||
            String(tipo).includes(filtroTexto);

        /* ── FILTRO DATA ──
           ✅ Corrige bug de fuso: parseia manualmente "YYYY-MM-DD"
           evitando que new Date() interprete como UTC e mude o dia
        ── */
        let matchData = true;

        if (filtroData) {

            const [anoF, mesF, diaF] = filtroData.split("-").map(Number);

            function mesmoDia(dataStr) {
                if (!dataStr) return false;
                const d = new Date(dataStr);
                return (
                    d.getFullYear() === anoF &&
                    d.getMonth() + 1 === mesF &&
                    d.getDate() === diaF
                );
            }

            matchData = mesmoDia(item.dataentrada) || mesmoDia(item.datasaida);
        }

        /* ── FILTRO TIPO ── */
        const mapaTipos = {
            ramal:        [2, 22],
            grupo:        [3, 32],
            pessoa:       [4, 42],
            grupocaptura: [5],
            outros:       [1],
            semcategoria: [] // tratado abaixo
        };

        let matchTipo = true;

        if (filtroTipo) {
            if (filtroTipo === "semcategoria") {
                const todosConhecidos = [1, 2, 3, 4, 5, 22, 32, 42];
                matchTipo = !todosConhecidos.includes(tipo);
            } else if (mapaTipos[filtroTipo]) {
                matchTipo = mapaTipos[filtroTipo].includes(tipo);
            }
        }

        return matchTexto && matchData && matchTipo;
    });

    preencherTabelaLixeira(filtrados);
}


/* =========================================================
   EVENTOS — todos chamam o filtro unificado
========================================================= */
document.addEventListener("DOMContentLoaded", () => {

    carregarLixeira();

    ["searchLixeira", "filterDate", "filtroTipo"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener(
            id === "searchLixeira" ? "input" : "change",
            filtrarLixeira
        );
    });
});

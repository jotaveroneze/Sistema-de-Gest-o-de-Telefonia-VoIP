async function carregarDepartamentos() {
    try {
        const response = await fetch('/departamento/listar');
        if (!response.ok) throw new Error("Erro ao buscar departamentos");
        window.departamentos = await response.json(); // global seguro
        renderTabelaDepartamentos(window.departamentos);
        carregarDepartamentosEditar();
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar departamentos");
    }
}

function renderTabelaDepartamentos(lista) {
    const tbody = document.querySelector("#tabelaDepartamentos tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    lista.forEach(dep => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><input type="radio" name="departamentoSelecionado" value="${dep.id}" ${dep.id === departamentoSelecionadoId ? "checked" : ""}></td>
            <td>${dep.sigla}</td>
            <td>${dep.nome}</td>
        `;
        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('input[name="departamentoSelecionado"]').forEach(radio => {
        radio.addEventListener('change', function() {
            departamentoSelecionadoId = parseInt(this.value);
            console.log("departamento:", departamentoSelecionadoId);
        });
    });
}

async function salvarNovoDepartamento() {
    const departamentoNome = document.getElementById("txtAddDepartamento").value.trim();
    const idsecretaria = window.secretariaSelecionadoId; // assumindo global

    if (!departamentoNome) { alert("Preencha o nome do departamento!"); return; }
    if (!idsecretaria) { alert("Preencha a secretaria!"); return; }

    try {
        const resposta = await fetch("/departamento/adicionar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome: departamentoNome, idsecretaria: parseInt(idsecretaria, 10) })
        });

        if (!resposta.ok) {
            const resultado = await resposta.json();
            alert("Erro ao adicionar departamento: " + (resultado.erro || resultado.mensagem));
            return;
        }

        document.getElementById("formAdicionar").reset();
        alert("Departamento adicionado com sucesso!");
        window.location.href = "/departamento";
    } catch (erro) {
        console.error("Erro ao adicionar departamento:", erro);
        alert("Erro ao adicionar departamento.");
    }
}

async function removerDepartamento(id) {
    if (!confirm("Tem certeza que deseja remover este departamento?")) return;

    try {
        const resposta = await fetch(`/departamento/remover/${id}`, { method: 'DELETE', headers: { 'Content-Type': 'application/json' } });
        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);
            carregarDepartamentos();
        } else {
            alert(dados.erro || "Erro ao desativar departamento");
        }
    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar departamento");
    }
}

function abrirAdicionarDepartamento() {
    abrirModal("modalAdicionarDepartamento");
}

// Search SEM variável (evita erro!)
document.getElementById("searchDepartamento")?.addEventListener("input", function () {
    const filtro = this.value.toLowerCase();
    document.querySelectorAll("#tabelaDepartamentos tbody tr").forEach(linha => {
        linha.style.display = linha.innerText.toLowerCase().includes(filtro) ? "" : "none";
    });
});

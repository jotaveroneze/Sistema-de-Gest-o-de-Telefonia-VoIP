//#region pessoa

function abrirAdicionarPessoa() {


    carregarPessoas()
    carregarDepartamentos()
    carregarVinculos()
    carregarEmpresas();

   abrirModal("modalAdicionarPessoa");
}

// Carregar pessoas do banco
async function carregarPessoas(page = 1) {
    mostrarLoadingTabela();
    try {
        const searchInput = document.getElementById("searchPessoa");
        const searchTerm = searchInput ? searchInput.value.trim() : '';

        const params = new URLSearchParams({
            page: page,
            per_page: 10
        });
        if (searchTerm) params.append('search', searchTerm);

        const response = await fetch(`/pessoa/listar?${params}`);
        if (!response.ok) throw new Error("Erro ao buscar pessoas");

        const data = await response.json();
        pessoas = data.pessoas;
        paginaAtual = data.page;

        preencherTabelaPessoas(pessoas);  // ✅ já protegida

        // ✅ Proteção TOTAL para TODOS os elementos
        const btnAnterior = document.getElementById('btnAnterior');
        const btnProxima = document.getElementById('btnProxima');
        const infoPaginacao = document.getElementById('infoPaginacao');
        const listaPaginas = document.getElementById('listaPaginas');

        if (btnAnterior) btnAnterior.disabled = !data.has_prev;
        if (btnProxima) btnProxima.disabled = !data.has_next;
        if (infoPaginacao) {
            infoPaginacao.textContent = `Página ${data.page} de ${data.pages} (${data.total})`;
        }

        if (listaPaginas) {
            renderizarPaginas(data.page, data.pages);
            atualizarBotoesPulo(data.page, data.pages);
        }

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar pessoas");
    } finally {
        esconderLoadingTabela();
    }
}


function atualizarBotoesPulo(paginaAtual, totalPaginas) {
    const btnRetroceder = document.getElementById('btnRetroceder');
    const btnAvancar = document.getElementById('btnAvancar');

    if (btnRetroceder) {
        btnRetroceder.disabled = paginaAtual <= 10;
        btnRetroceder.onclick = () => carregarPessoas(Math.max(1, paginaAtual - 10));
    }

    if (btnAvancar) {
        btnAvancar.disabled = paginaAtual >= totalPaginas - 10;
        btnAvancar.onclick = () => carregarPessoas(Math.min(totalPaginas, paginaAtual + 10));
    }
}


function renderizarPaginas(paginaAtual, totalPaginas) {
    const ul = document.getElementById('listaPaginas');
    ul.innerHTML = '';

    if (totalPaginas <= 1) return;

    // Sempre mostra 1 e última
    adicionarPagina(ul, 1, paginaAtual);

    // Se >3 páginas, mostra reticências
    if (paginaAtual > 3) {
        const li = document.createElement('li');
        li.className = 'page-item disabled';
        li.innerHTML = '<span class="page-link">...</span>';
        ul.appendChild(li);
    }

    // Páginas próximas (±2)
    for (let p = Math.max(2, paginaAtual - 2); p <= Math.min(totalPaginas - 1, paginaAtual + 2); p++) {
        adicionarPagina(ul, p, paginaAtual);
    }

    if (paginaAtual < totalPaginas - 2) {
        const li = document.createElement('li');
        li.className = 'page-item disabled';
        li.innerHTML = '<span class="page-link">...</span>';
        ul.appendChild(li);
    }

    adicionarPagina(ul, totalPaginas, paginaAtual);
}

function adicionarPagina(ul, pagina, atual) {
    const li = document.createElement('li');
    li.className = 'page-item' + (pagina === atual ? ' active' : '');
    li.innerHTML = `<button class="page-link">${pagina}</button>`;
    li.querySelector('button').onclick = () => carregarPessoas(pagina);
    ul.appendChild(li);
}


async function carregarTodasPessoas() {
    try {
        const res = await fetch('/pessoa/todas');
        todasPessoas = await res.json();  // Salva global
    } catch(e) {
        console.warn('Não carregou todas:', e);
    }
}


// ✅ Adicione estes event listeners (no final do JS)
document.getElementById('btnAnterior')?.addEventListener('click', () => carregarPessoas(paginaAtual - 1));
document.getElementById('btnProxima')?.addEventListener('click', () => carregarPessoas(paginaAtual + 1));

function atualizarInfoPaginacao(data) {
    const infoEl = document.getElementById('infoPaginacao') ||
                   document.querySelector('.paginacao-info');
    if (infoEl) {
        infoEl.textContent = `Página ${data.page} de ${data.pages} (${data.total})`;
    }
}

// Remover pessoa do backend
async function removerPessoa(idpessoa) {
    const confirmacao = confirm("Tem certeza que deseja remover esta pessoa?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/pessoa/remover/${idpessoa}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);

            // Remove a linha da tabela
            const linha = document.getElementById(`pessoa-${idpessoa}`);
            if (linha) linha.remove();

            carregarPessoas(); // Atualiza tabela
        } else {
            alert(dados.erro || "Erro ao desativar pessoa");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar pessoa");
    }
}


function preencherTabelaPessoas(lista) {
    const tabela = document.getElementById("tabelaPessoa");
     if (!tabela) {
        console.warn("Tabela #tabelaPessoa não encontrada. Pulando...");
        return;
    }
    tabela.innerHTML = "";

    lista.forEach(p => {
        tabela.innerHTML += `
            <tr>
                <td>
                <button class="btn btn-link p-0 ms-1" 
                        onclick="copiar('${p.nome}')" 
                        title="Copiar nome">
                    <i class="fa-solid fa-copy fa-sm"></i>
                </button>
                ${p.nome}</td>
                <td>
                <button class="btn btn-link p-0 ms-1" 
                        onclick="copiar('${p.funcional}')" 
                        title="Copiar funcional">
                    <i class="fa-solid fa-copy fa-sm"></i>
                </button>
                ${p.funcional}</td>
                <td>
                <button class="btn btn-link p-0 ms-1" 
                        onclick="copiar('${p.cpf}')" 
                        title="Copiar CPF">
                    <i class="fa-solid fa-copy fa-sm"></i>
                </button>
                ${p.cpf}</td>
                <td>${p.vinculo}</td>
                <td>${p.secretaria}</td>
                <td>${p.departamento}</td>
                <td>${p.empresa}</td>

                <td>
                    <button class="btn btn-warning btn-sm"
                        data-bs-toggle="tooltip"
                        data-bs-placement="top"
                        title="Editar pessoa"
                        onclick="abrirEditarPessoa(${p.id})">
                        <i class="fa-solid fa-pen"></i>
                    </button>

                    <button class="btn btn-danger btn-sm"
                        data-bs-toggle="tooltip"
                        data-bs-placement="top"
                        title="Excluir pessoa"
                        onclick="removerPessoa(${p.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}
function copiar(texto) {
    navigator.clipboard.writeText(texto)
        .catch(err => console.error("Erro ao copiar:", err));
}

// SUBSTITUA pessoas.filter por todasPessoas.filter
document.getElementById("searchPessoa")?.addEventListener("input", debounce(function() {
    paginaAtual = 1;
    carregarPessoas(1);
}, 300));

// ✅ Adicione debounce (topo JS)
function debounce(func, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}





async function salvarNovoPessoa() {

    const pessoaNome     = document.getElementById("txtAddNome").value.trim();
    const pessoaFuncional = document.getElementById("txtAddFuncional").value.trim();
    const pessoaCPF      = document.getElementById("txtAddCPF").value.trim();
    const idvinculo      = document.getElementById("txtAddVinculo").value;

    if (!idvinculo)       { alert("Selecione o Vínculo!");      return; }
    if (!departamentoSelecionadoId) { alert("Selecione o Departamento!"); return; }
    if (!empresaSelecionadoId)      { alert("Selecione a Empresa!");      return; }

    try {
        const resposta = await fetch("/pessoa/adicionar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                nome:          pessoaNome,
                funcional:     pessoaFuncional,
                cpf:           pessoaCPF,
                idvinculo:     parseInt(idvinculo, 10),                  // ✅ inteiro
                iddepartamento: parseInt(departamentoSelecionadoId, 10), // ✅ inteiro
                idempresa:     parseInt(empresaSelecionadoId, 10)        // ✅ inteiro
            })
        });

        // ✅ verifica ok antes de parsear JSON
        if (!resposta.ok) {
            const resultado = await resposta.json();
            alert("Erro ao adicionar pessoa: " + (resultado.erro || resultado.mensagem));
            return;
        }

        // ✅ todo o cleanup antes do redirect
        const modal = bootstrap.Modal.getInstance(document.getElementById("modalAdicionarPessoa"));
        if (modal) modal.hide();
        document.getElementById("formAdicionar").reset();

        alert("Pessoa adicionada com sucesso!"); // ✅ grafia correta

        window.location.href = "/pessoas"; // ✅ redirect por último

    } catch (erro) {
        console.error("Erro ao adicionar pessoa:", erro);
        alert("Erro ao adicionar pessoa.");
    }
}


// Função para salvar edição
async function salvarEdicaoPessoa() {
  const id = document.getElementById("editIdPessoa").value;
  const nome = document.getElementById("editNome").value.trim();
  const funcional = document.getElementById("editFuncional").value.trim();
  const cpf = document.getElementById("editCPF").value.trim();
  const vinculo = document.getElementById("editVinculo").value;

  if (!nome) {
    alert("O nome é obrigatório!");
    return;
  }

  if (!funcional) {
    alert("O funcional é obrigatório!");
    return;
  }

  if (!cpf) {
    alert("O CPF é obrigatório!");
    return;
  }

  if (!vinculo) {
    alert("Selecione o vínculo!");
    return;
  }

  // Se essas variáveis não existirem no escopo, vai dar ReferenceError (declare-as fora da função com let) [web:93]
  const iddepartamento = (typeof departamentoSelecionadoEditarId !== "undefined")
    ? departamentoSelecionadoEditarId
    : null;

  if (!iddepartamento) {
    alert("Selecione o Departamento!");
    return;
  }

  const idempresa = (typeof empresaSelecionadoEditarId !== "undefined")
    ? empresaSelecionadoEditarId
    : null;

  if (!idempresa) {
    alert("Selecione a Empresa!");
    return;
  }

  const dados = {
    nome,
    funcional,
    cpf,
    idvinculo: vinculo,
    iddepartamento,
    idempresa
  };

  try {
    const resposta = await fetch(`/pessoa/editar/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados)
    });

    // Não tentar parsear JSON se a resposta vier vazia ou não for JSON (evita "Unexpected end of JSON input") [web:96][web:76]
    let resultado = null;
    const contentType = resposta.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
      resultado = await resposta.json();
    } else {
      const texto = await resposta.text();
      resultado = texto ? { mensagem: texto } : null;
    }

    if (!resposta.ok) {
      alert("Erro ao atualizar: " + ((resultado && (resultado.erro || resultado.mensagem)) || "Erro ao atualizar"));
      return;
    }

    alert("Atualizado com sucesso!");
    window.location.href = "/pessoas"; // redireciona após salvar [web:87]
    return;

  } catch (erro) {
    console.error("Erro ao editar:", erro);
    alert("Erro ao editar registro.");
  }
}


function abrirEditarPessoa(id) {

    const pessoa = pessoas.find(x => x.id === id);
    if (!pessoa) return alert("Pessoa não encontrada!");

    // Preenche os campos básicos
    document.getElementById("editIdPessoa").value = pessoa.id;
    document.getElementById("editNome").value = pessoa.nome;
    document.getElementById("editFuncional").value = pessoa.funcional;
    document.getElementById("editCPF").value = pessoa.cpf;

    // Selecionar o vínculo
    carregarVinculosEditar(pessoa.idvinculo);
    //carregarEmpresasEditar(pessoa.idempresa);

    // Preencher a tabela de departamentos e marcar o atual
    carregarDepartamentosEditar(pessoa.iddepartamento);
    carregarEmpresasEditar();

    // Preencher empresas e marcar a atual
    //carregarEmpresasEditar(pessoa.idempresa);

    // Abre o modal
    new bootstrap.Modal(document.getElementById("modalEditar")).show();
}


// ================================ VINCULOS ================================================


function carregarVinculos() {
    fetch("/vinculo/listar")
        .then(res => res.json())
        .then(data => {

            const select = document.getElementById("txtAddVinculo");
            select.innerHTML = "";

            data.forEach(v => {
                const option = document.createElement("option");
                option.value = v.id;
                option.textContent = v.nome;

                // 🔥 Servidor (id = 1) como padrão
                if (Number(v.id) === 1) {
                    option.selected = true;
                }

                select.appendChild(option);
            });
        })
        .catch(err => console.error("Erro ao carregar vínculos:", err));
}


function carregarVinculosEditar(vinculoSelecionado) {
    fetch("/vinculo/listar")
        .then(res => res.json())
        .then(vinculos => {
            const select = document.getElementById("editVinculo");
            select.innerHTML = "";

            vinculos.forEach(v => {
                select.innerHTML += `
                    <option value="${v.id}" ${Number(v.id) === Number(vinculoSelecionado) ? "selected" : ""}>
                        ${v.nome}
                    </option>
                `;
            });
        });
}

// FILTRAR SECRETARIAS NO MODAL EDITAR
const searchSecretariaEditar = document.getElementById("searchSecretariaEditar");
if (searchSecretariaEditar) {
    searchSecretariaEditar.addEventListener("input", function () {
        let filtro = this.value.toLowerCase();
        let linhas = document.querySelectorAll("#tabelaSecretariaEditar tbody tr");
        linhas.forEach(linha => {
            let texto = linha.innerText.toLowerCase();
            linha.style.display = texto.includes(filtro) ? "" : "none";
        });
    });
}

// FILTRAR SECRETARIAS NO MODAL EDITAR
const searchSecretaria = document.getElementById("searchSecretaria");
if (searchSecretaria) {
    searchSecretaria.addEventListener("input", function () {
        let filtro = this.value.toLowerCase();
        let linhas = document.querySelectorAll("#tabelaSecretaria tbody tr");
        linhas.forEach(linha => {
            let texto = linha.innerText.toLowerCase();
            linha.style.display = texto.includes(filtro) ? "" : "none";
        });
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    await carregarTodasPessoas();  // ✅ PRIMEIRO todas
    carregarPessoas(1);            // DEPOIS página 1
    carregarDepartamentos();
    carregarVinculos();
    carregarEmpresas();
});




//#endregion

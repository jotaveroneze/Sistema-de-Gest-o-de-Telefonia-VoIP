document.addEventListener("DOMContentLoaded", initHome);

function initHome() {
  carregarDashboard();
  chamarFuncoesDaTela();
}

function carregarDashboard() {
  fetch("/api/dashboard", { credentials: "same-origin" })
    .then(res => {
      if (!res.ok) throw new Error("Erro na resposta da API");
      return res.json();
    })
    .then(atualizarDashboard)
    .catch(err => console.error("Erro dashboard:", err));
}

function atualizarDashboard(data) {
  atualizarSeExiste("totalPessoa", data.pessoa);
  atualizarSeExiste("totalTelefone", data.telefone);
  atualizarSeExiste("telefonesEntregues", data.telefones_entregues);
  atualizarSeExiste("telefonesNaoEntregues", data.telefones_nao_entregues);
  atualizarSeExiste("ramalVago", data.ramais_livres);
  atualizarSeExiste("ramalNaoVago", data.ramais_em_uso);
  atualizarSeExiste("span-telefones-defeito", data.grupo_pendente);
  atualizarSeExiste("span-ramal-pendente", data.ramal_pendente);
  atualizarSeExiste("span-pessoa-pendente", data.pessoa_pendente);
  atualizarSeExiste("span-outras-pendencias", data.outras_pendencias);
}

function atualizarSeExiste(id, valor) {
  const el = document.getElementById(id);
  if (el) el.textContent = valor ?? 0;
}

function chamarFuncoesDaTela() {
  const funcoes = [
    "carregarEmpresas",
    "carregarPessoas",
    "carregarDepartamento",
    "carregarSecretarias",
    "carregarVinculos",
    "carregarLugarTelefone",
    "carregarModelo",
    "carregarOperadoras",
    "carregarTroncoModal",
    "carregarTroncoEditar",
    "carregarRamal"
  ];

  funcoes.forEach(chamarSeExiste);
}

function chamarSeExiste(nomeFuncao) {
  if (typeof window[nomeFuncao] === "function") {
    window[nomeFuncao]();
  }
}

function irParaRamal(aba) {
  window.location.href = `/ramal?aba=${aba}`;
}
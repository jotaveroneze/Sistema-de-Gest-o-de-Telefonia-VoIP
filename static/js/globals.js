let departamentos = []; // array global
let departamentoSelecionadoId = null; // id do departamento selecionado
let departamentoSelecionadoEditarId

let empresas = [];
let empresaSelecionadoId = null;
let empresaSelecionadoEditarId = null;

let operadoras = [];                     // array global
let operadoraSelecionadaId = null;       // seleção no modal adicionar
let operadoraSelecionadaEditarId = null; // seleção no modal editar

let ramal = [];
let ramais = [];
let ramalVago = [];
let ramalEmUso = [];
let ramalDetalhe = [];
let ramalAtivoId = null;
let ramalAtivoTexto = "";

let secretarias = []; // array global
let secretariaSelecionadoId = null;
let secretariaSelecionadoEditarId = null;

let troncos = [];
let troncoSelecionadoId = null;

let modelos = []; // array global

let todasPessoas = [];  // ✅ NOVO: Todas pessoas
let pessoas = [];       // Página atual
let paginaAtual = 1;
const PER_PAGE = 10;
const PER_PAGE_TELEFONES = 5;

let listaUsuarios = [];

let numerosgrupo = [];

let grupocapturas = [];

// ids selecionados
let grupocapturaSelecionadoId = null;
let grupocapturaSelecionadoEditarId = null;


let ramalnumerogrupo = [];
let ramaisSelecionados = [];
let ramaisDisponiveis = [];
let ramalnumerogrupoSelecionadoId = null;
let modalVisualizarRamalNumeroGrupo = null;
let numeroGrupoAtivoId = null;
let numeroGrupoAtivoTexto = null;
let numerosGrupoDisponiveis = [];
let numerosGrupoSelecionados = [];

let telefones = [];
let telefoneEditarId = null;
let modeloSelecionadoId = null;
let lugarTelefoneSelecionadoId = null;
let modeloSelecionadoEditarId = null;
let lugarTelefoneSelecionadoEditarId = null;

let idRamalAtual = null
let numeroRamalAtual = null;

let pessoasSelecionadas = new Set();
let telefonesSelecionados = new Set();
let ramalSelecionadoId = null;

let telefoneAtivoId = null;
let telefoneAtivoTexto = null;
let telefoneAtivoSerialTexto = null

let telefonePessoaAtual = null;
let pessoasDisponiveis = [];

let proximoModalId = null;
const modalStack = [];

let modalVisualizarGrupoCapturaInstance = null;
let modalVisualizarPessoasTelefoneInstance = null;
let modalVisualizarRamaisTelefoneInstance = null;

let pendencias = [];

let logs = [];

let lugartelefones = [];
let lugarTelefoneEditarId = null;

function mostrarLoadingTabela() {
  try {
    document.getElementById("loadingTabela").classList.remove("d-none");
    document.querySelector(".tabela-container").classList.add("d-none");
  } catch (erro) {

  }
}


function esconderLoadingTabela() {
  try {
    document.getElementById("loadingTabela").classList.add("d-none");
    document.querySelector(".tabela-container").classList.remove("d-none");
  } catch (erro) {

  }
}


/**
 * Fecha todos os modais abertos do Bootstrap 5 e força uma limpeza
 * do ambiente para evitar o problema de "tela travada".
 * Testado e otimizado para Bootstrap v5.3.x.
 */
function fecharModais() {

}


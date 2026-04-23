// --- VARIÁVEIS GLOBAIS ---
// Mantém o controle da sequência de modais abertos.

// Guarda o ID do próximo modal a ser aberto durante uma troca.


// --- FUNÇÃO PRINCIPAL PARA ABRIR MODAIS ---
function abrirModal(modalId) {
    const modalAtivoEl = document.querySelector('.modal.show');

    // Se já existe um modal visível na tela...
    if (modalAtivoEl) {
        // 1. Marcamos qual será o próximo modal a ser aberto.
        proximoModalId = modalId;

        // 2. Adicionamos o ID do modal ativo à pilha para poder voltar a ele depois.
        modalStack.push(modalAtivoEl.id);

        // 3. Pegamos a instância do Bootstrap e iniciamos o processo de fechamento.
        const instanciaModalAtivo = bootstrap.Modal.getInstance(modalAtivoEl);
        if (instanciaModalAtivo) {
            instanciaModalAtivo.hide();
        }
    } else {
        // Se não há nenhum modal aberto, simplesmente abre o novo.
        const modalEl = document.getElementById(modalId);
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    }
}

// --- GERENCIADOR DE EVENTOS GLOBAL PARA TODOS OS MODAIS ---
// Usamos delegação de eventos para ouvir o fechamento de qualquer modal no documento.
document.addEventListener('hidden.bs.modal', (event) => {
    // 'event.target' é o elemento do modal que acabou de ser fechado.
    const modalFechadoEl = event.target;

    // CASO 1: Estamos trocando de um modal para outro.
    if (proximoModalId) {
        const modalParaAbrirEl = document.getElementById(proximoModalId);
        if (modalParaAbrirEl) {
            const modal = new bootstrap.Modal(modalParaAbrirEl);
            modal.show();
        }
        // Limpa a variável para o próximo ciclo.
        proximoModalId = null;
        return; // Encerra a execução aqui.
    }

    // CASO 2: Um modal foi fechado (pelo 'X' ou 'Esc') e precisamos voltar para o anterior.
    if (modalStack.length > 0) {
        // Remove o ID do modal que acabou de ser fechado da pilha.
        // (Assumindo que o último da pilha é o que foi fechado para chegar aqui)
        if (modalStack[modalStack.length - 1] === modalFechadoEl.id) {
           // Esta verificação pode ser redundante dependendo da sua lógica exata,
           // mas garante que não estamos removendo o item errado da pilha.
        }

        // Pega o ID do modal anterior que precisa ser reaberto.
        const modalAnteriorId = modalStack.pop();
        const modalAnteriorEl = document.getElementById(modalAnteriorId);
        if (modalAnteriorEl) {
            const modalAnterior = new bootstrap.Modal(modalAnteriorEl);
            modalAnterior.show();
        }
    }
});

function fecharModaisVinculo() {
    const modalAberto = document.querySelector('.modal.show');

    if (modalAberto) {
        const modalInstance = bootstrap.Modal.getInstance(modalAberto);
        if (modalInstance) {
            modalInstance.hide();
        }
    }
}
function fecharModais(){}
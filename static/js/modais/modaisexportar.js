document.addEventListener("DOMContentLoaded", function () {

  const btnExportar = document.getElementById("btnConfirmarExportacao");
  const form = document.getElementById("formExportar");

  if (!btnExportar || !form) return;

  btnExportar.addEventListener("click", function () {

    const selecionados = form.querySelectorAll(
      'input[name="exportar"]:checked'
    );

    if (selecionados.length === 0) {
      alert("Selecione ao menos uma opção para exportar.");
      return;
    }

    // Envio padrão do form (necessário para download)
    form.submit();

  });

});

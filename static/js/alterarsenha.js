document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(".tela-alterarSenha");
    const novaSenha = document.querySelector("input[name='novasenha']");
    const confirmarSenha = document.querySelector("input[name='confirmarsenha']");

    let erro = document.querySelector(".mensagem-erro");
    if (!erro) {
        erro = document.createElement("p");
        erro.classList.add("mensagem-erro");
        erro.style.color = "red";
        erro.style.marginTop = "10px";
        form.appendChild(erro);
        erro.style.display = "none";
    }

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        if (novaSenha.value.trim() === "" || confirmarSenha.value.trim() === "") {
            erro.textContent = "Preencha todos os campos.";
            erro.style.display = "block";
            return;
        }

        if (novaSenha.value !== confirmarSenha.value) {
            erro.textContent = "As senhas não coincidem.";
            erro.style.display = "block";
            return;
        }

        erro.style.display = "none";

        // 🔥 Envia para a rota Flask
        const resposta = await fetch("/alterarsenha/alterar_senha", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                senha: novaSenha.value
            })
        });

        const resultado = await resposta.json();

        if (resultado.ok) {
            alert("Senha alterada com sucesso!");
            window.location.href = "/home";
        } else {
            erro.textContent = resultado.mensagem || "Erro ao alterar a senha.";
            erro.style.display = "block";
        }
    });
});

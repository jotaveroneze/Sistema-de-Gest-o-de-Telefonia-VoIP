const nome  = "{{ user_nome }}";
const email = "{{ user_email }}";

// ✅ opção 1 — guard explícito
const elNome  = document.getElementById("userNome");
const elEmail = document.getElementById("userEmail");

if (elNome)  elNome.textContent  = nome  || "Usuário";
if (elEmail) elEmail.textContent = email || "email@dominio.com";

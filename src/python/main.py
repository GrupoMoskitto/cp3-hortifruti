import json
import unicodedata
from datetime import datetime

from pyscript import document

# ===== Carregamento dos dados =====
with open("dados.json", encoding="utf-8") as arquivo:
    dados = json.load(arquivo)

frutas = dados["frutas"]

# ===== Telemetria =====
eventos = []

def registrar(evento):
    hora = datetime.now().strftime("%H:%M:%S")
    eventos.append(f"[{hora}] {evento}")
    lista = document.querySelector("#telemetria")
    lista.innerHTML = ""
    for item in reversed(eventos[-8:]):  # 8 mais recentes, novo no topo
        li = document.createElement("li")
        li.innerText = item
        lista.appendChild(li)

# ===== Catálogo =====
def renderizar_catalogo():
    grade = document.querySelector("#grade-frutas")
    grade.innerHTML = ""
    for f in frutas:
        card = document.createElement("div")
        card.className = "card-fruta"
        card.id = f"fruta-{f['id']}"
        card.innerHTML = f"""
            <img src="{f['imagem']}" alt="{f['nome']}">
            <h3>{f['nome']}</h3>
            <p>R$ {f['preco']:.2f} / {f['unidade']}</p>
            <p>Estoque: {f['estoque']}</p>
        """
        grade.appendChild(card)
    registrar(f"Catálogo carregado com {len(frutas)} frutas")

renderizar_catalogo()
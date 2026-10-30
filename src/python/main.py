import json
import unicodedata
from datetime import datetime
import numpy as np

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

# ===== Guardrails =====
def normalizar(texto):
    """Remove acentos e deixa minúsculo: 'Maçã' -> 'maca'"""
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn").lower().strip()

def validar_entrada(texto):
    if not texto.strip():
        return "Digite o nome de uma fruta."
    if len(texto) > 30:
        return "Busca muito longa (máx. 30 caracteres)."
    if not texto.replace(" ", "").isalpha():
        return "Use apenas letras."
    return None  # entrada válida

def mostrar_mensagem(texto, tipo):
    msg = document.querySelector("#mensagem-guardrail")
    msg.innerText = texto
    msg.className = f"mensagem {tipo}"

def buscar(event):
    entrada = document.querySelector("#entrada-busca").value

    erro = validar_entrada(entrada)
    if erro:
        mostrar_mensagem(erro, "erro")
        registrar(f"Guardrail bloqueou: '{entrada}'")
        return

    for card in document.querySelectorAll(".card-fruta"):
        card.classList.remove("destaque")

    termo = normalizar(entrada)
    fruta = next((f for f in frutas if normalizar(f["nome"]) == termo), None)

    if fruta is None:
        mostrar_mensagem("Fruta não encontrada no catálogo.", "erro")
        registrar(f"Busca sem resultado: '{entrada}'")
        return

    mostrar_mensagem(f"{fruta['nome']} encontrada!", "ok")
    document.querySelector(f"#fruta-{fruta['id']}").classList.add("destaque")
    registrar(f"Busca: {fruta['nome']}")

# ===== Embeddings: Norma Euclidiana =====
def analisar_vetores(fruta_base):
    base = np.array(fruta_base["embedding"])
    norma = np.linalg.norm(base)  # sqrt(x² + y² + z²)

    html = f"<p><b>{fruta_base['nome']}</b> {base.tolist()} → norma = {norma:.3f}</p>"

    distancias = []
    for f in frutas:
        if f["id"] == fruta_base["id"]:
            continue
        dist = np.linalg.norm(base - np.array(f["embedding"]))
        distancias.append((dist, f["nome"]))

    distancias.sort()
    for dist, nome in distancias:
        html += f"<p>{nome}: distância {dist:.3f}</p>"
    html += f"<p>🍓 Mais parecida: <b>{distancias[0][1]}</b></p>"

    document.querySelector("#resultado-vetor").innerHTML = html
    registrar(f"Norma calculada para {fruta_base['nome']}")

    
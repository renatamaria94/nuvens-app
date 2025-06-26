# isso para rodar:
# python -m streamlit run app.py
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import json

# Configuração inicial
st.set_page_config(layout="wide")
st.title("☁️ Nuvens de Sonhos e Pesadelos")

# Funções utilitárias
def carregar_respostas(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_respostas(nome_arquivo, lista):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(lista, f)

# Arquivos de armazenamento
ARQ_SONHOS = "sonhos.json"
ARQ_PESADELOS = "pesadelos.json"

# Carrega dados existentes
sonhos = carregar_respostas(ARQ_SONHOS)
pesadelos = carregar_respostas(ARQ_PESADELOS)

# Entrada dos usuários
with st.form("formulario"):
    col1, col2 = st.columns(2)
    with col1:
        entrada_sonho = st.text_input("💭 Quais são seus sonhos?")
    with col2:
        entrada_pesadelo = st.text_input("😨 Quais são seus pesadelos?")
    enviado = st.form_submit_button("Enviar")

# Atualiza as listas
if enviado:
    if entrada_sonho:
        sonhos.extend(entrada_sonho.split())
        salvar_respostas(ARQ_SONHOS, sonhos)
    if entrada_pesadelo:
        pesadelos.extend(entrada_pesadelo.split())
        salvar_respostas(ARQ_PESADELOS, pesadelos)
    st.success("Respostas registradas com sucesso!")

# Gera e exibe as nuvens
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌈 Nuvem dos Sonhos")
    if sonhos:
        texto_sonhos = " ".join(sonhos)
        wc_sonhos = WordCloud(width=600, height=400, background_color="white").generate(texto_sonhos)
        fig1, ax1 = plt.subplots()
        ax1.imshow(wc_sonhos, interpolation="bilinear")
        ax1.axis("off")
        st.pyplot(fig1)
    else:
        st.info("Nenhum sonho enviado ainda.")

with col2:
    st.subheader("🌩️ Nuvem dos Pesadelos")
    if pesadelos:
        texto_pesadelos = " ".join(pesadelos)
        wc_pesadelos = WordCloud(width=600, height=400, background_color="black", colormap="Reds").generate(texto_pesadelos)
        fig2, ax2 = plt.subplots()
        ax2.imshow(wc_pesadelos, interpolation="bilinear")
        ax2.axis("off")
        st.pyplot(fig2)
    else:
        st.info("Nenhum pesadelo enviado ainda.")

# Área restrita: Modo administrador
with st.expander("🔐 Acesso restrito (admin)"):
    senha = st.text_input("Digite a senha para acessar funções administrativas:", type="password")
    if senha == "minhasenha123":  # 🔒 Altere aqui sua senha pessoal
        st.success("Acesso autorizado.")
        if st.button("🗑️ Limpar todas as respostas"):
            salvar_respostas(ARQ_SONHOS, [])
            salvar_respostas(ARQ_PESADELOS, [])
            st.rerun()
    elif senha != "":
        st.error("Senha incorreta.")

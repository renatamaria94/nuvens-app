# isso para rodar:
# python -m streamlit run app.py
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import json
import pandas as pd
from datetime import datetime
from io import BytesIO
import unicodedata
import string

# Configuração inicial
st.set_page_config(layout="wide")
st.title("☁️ Nuvens de Sonhos e Pesadelos")

# Stopwords simples em português
stopwords = {
    "de", "do", "da", "das", "dos", "em", "e", "o", "a", "os", "as", "que",
    "com", "por", "para", "no", "na", "nos", "nas", "um", "uma", "é", "ser",
    "ao", "se", "são", "foi", "sou", "já", "ou", "mas", "me", "minha"
}

# Função para limpar e processar palavras
def limpar_palavras(lista):
    palavras_limpa = []
    for palavra in lista:
        palavra = palavra.lower()
        palavra = unicodedata.normalize("NFKD", palavra).encode("ASCII", "ignore").decode("utf-8")
        palavra = "".join(ch for ch in palavra if ch.isalpha())
        if palavra and palavra not in stopwords:
            palavras_limpa.append(palavra)
    return palavras_limpa

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
ARQ_PLANILHA = "respostas.csv"

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

# Processa entrada do usuário
if enviado:
    if entrada_sonho:
        palavras_sonho = limpar_palavras(entrada_sonho.split())
        sonhos.extend(palavras_sonho)
        salvar_respostas(ARQ_SONHOS, sonhos)
    if entrada_pesadelo:
        palavras_pesadelo = limpar_palavras(entrada_pesadelo.split())
        pesadelos.extend(palavras_pesadelo)
        salvar_respostas(ARQ_PESADELOS, pesadelos)

    # Registro na planilha com hora (mantém texto original)
    nova_resposta = {
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sonho": entrada_sonho,
        "pesadelo": entrada_pesadelo
    }

    if os.path.exists(ARQ_PLANILHA):
        df = pd.read_csv(ARQ_PLANILHA)
        df = pd.concat([df, pd.DataFrame([nova_resposta])], ignore_index=True)
    else:
        df = pd.DataFrame([nova_resposta])
    df.to_csv(ARQ_PLANILHA, index=False)

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
    if senha == "seplan123":  
        st.success("Acesso autorizado.")

        # Visualizar a planilha
        if os.path.exists(ARQ_PLANILHA):
            df_download = pd.read_csv(ARQ_PLANILHA)
            st.subheader("📋 Respostas registradas")
            st.dataframe(df_download, use_container_width=True)

            # Botão de download
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_download.to_excel(writer, index=False, sheet_name='Respostas')
            st.download_button(
                label="⬇️ Baixar planilha de respostas (.xlsx)",
                data=buffer.getvalue(),
                file_name="respostas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Nenhuma resposta registrada ainda.")

        # Limpar nuvens
        if st.button("🗑️ Limpar todas as palavras"):
            salvar_respostas(ARQ_SONHOS, [])
            salvar_respostas(ARQ_PESADELOS, [])
            st.rerun()

        # Resetar planilha
        if st.button("🗑️ Resetar a planilha de respostas"):
            if os.path.exists(ARQ_PLANILHA):
                os.remove(ARQ_PLANILHA)
                st.success("Planilha apagada com sucesso.")
            else:
                st.warning("Nenhuma planilha para apagar.")
    elif senha != "":
        st.error("Senha incorreta.")


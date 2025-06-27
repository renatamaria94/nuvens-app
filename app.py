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
import requests  # <- necessário para enviar ao sheet.best

# CONFIGURAÇÃO INICIAL
st.set_page_config(layout="wide")
st.title("☁️ Nuvens de Sonhos e Pesadelos")

# Stopwords simples
stopwords = {
    "de", "do", "da", "das", "dos", "em", "e", "o", "a", "os", "as", "que",
    "com", "por", "para", "no", "na", "nos", "nas", "um", "uma", "é", "ser",
    "ao", "se", "são", "foi", "sou", "já", "ou", "mas", "me", "minha"
}

# Limpeza de palavras
def limpar_palavras(lista):
    palavras_limpa = []
    for palavra in lista:
        palavra = palavra.lower()
        palavra = unicodedata.normalize("NFKD", palavra).encode("ASCII", "ignore").decode("utf-8")
        palavra = "".join(ch for ch in palavra if ch.isalpha())
        if palavra and palavra not in stopwords:
            palavras_limpa.append(palavra)
    return palavras_limpa

# Arquivos locais
ARQ_SONHOS = "sonhos.json"
ARQ_PESADELOS = "pesadelos.json"
ARQ_PLANILHA = "respostas.csv"

# Funções locais
def carregar_respostas(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_respostas(nome_arquivo, lista):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(lista, f)

# Carrega palavras
sonhos = carregar_respostas(ARQ_SONHOS)
pesadelos = carregar_respostas(ARQ_PESADELOS)

# Formulário
st.subheader("📨 Compartilhe seus pensamentos")
with st.form(key="formulario_completo_2025"):
    col1, col2 = st.columns(2)
    with col1:
        entrada_sonho = st.text_input("💭 Quais são seus sonhos?")
    with col2:
        entrada_pesadelo = st.text_input("😨 Quais são seus pesadelos?")
    enviado = st.form_submit_button("Enviar")

# Processamento
if enviado:
    if entrada_sonho:
        palavras_sonho = limpar_palavras(entrada_sonho.split())
        sonhos.extend(palavras_sonho)
        salvar_respostas(ARQ_SONHOS, sonhos)
    if entrada_pesadelo:
        palavras_pesadelo = limpar_palavras(entrada_pesadelo.split())
        pesadelos.extend(palavras_pesadelo)
        salvar_respostas(ARQ_PESADELOS, pesadelos)

    nova_resposta = {
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sonho": entrada_sonho,
        "pesadelo": entrada_pesadelo
    }

    # Atualiza CSV local
    if os.path.exists(ARQ_PLANILHA):
        df = pd.read_csv(ARQ_PLANILHA)
        df = pd.concat([df, pd.DataFrame([nova_resposta])], ignore_index=True)
    else:
        df = pd.DataFrame([nova_resposta])
    df.to_csv(ARQ_PLANILHA, index=False)

    # Envia para Sheet.best
    url_sheetbest = "https://sheet.best/api/sheets/710efa5f-dc88-4da9-bbdd-decbf74edc99"  # <-- insira seu link aqui
    try:
        response = requests.post(url_sheetbest, json=nova_resposta)
        if response.status_code == 200:
            st.success("✅ Resposta registrada e enviada com sucesso!")
        else:
            st.warning("⚠️ Resposta salva localmente, mas falhou o envio para planilha.")
    except:
        st.warning("⚠️ Resposta salva localmente, mas ocorreu erro na conexão com a planilha.")

# Geração das nuvens
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

# Área de Administração
with st.expander("🔐 Acesso restrito (admin)"):
    senha = st.text_input("Digite a senha para acessar funções administrativas:", type="password")
    if senha == "seplan123":
        st.success("Acesso autorizado.")

        if os.path.exists(ARQ_PLANILHA):
            df_admin = pd.read_csv(ARQ_PLANILHA)
            st.subheader("📋 Respostas registradas")
            st.dataframe(df_admin, use_container_width=True)

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_admin.to_excel(writer, index=False, sheet_name='Respostas')
            st.download_button(
                label="⬇️ Baixar planilha de respostas (.xlsx)",
                data=buffer.getvalue(),
                file_name="respostas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        if st.button("🗑️ Limpar todas as palavras"):
            salvar_respostas(ARQ_SONHOS, [])
            salvar_respostas(ARQ_PESADELOS, [])
            st.rerun()

        if st.button("🗑️ Resetar a planilha de respostas"):
            if os.path.exists(ARQ_PLANILHA):
                os.remove(ARQ_PLANILHA)
                st.success("Planilha apagada com sucesso.")
            else:
                st.warning("Nenhuma planilha para apagar.")
    elif senha != "":
        st.error("Senha incorreta.")

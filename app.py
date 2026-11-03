import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Dashboard IBGE - Meios de Transporte",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

caminho_transporte_padrao = r"Tabela_13_Meio_de_transporte.xlsx"

# ==============================================================================
# 2. FUNÇÃO DE LEITURA E LIMPEZA COM PANDAS
# ==============================================================================
@st.cache_data
def carregar_e_limpar_transporte(caminho_ou_arquivo):
    """Lê a Tabela 13 (Excel ou CSV) e devolve seus percentuais tratados."""
    if isinstance(caminho_ou_arquivo, str):
        if caminho_ou_arquivo.lower().endswith(".csv"):
            bruto = pd.read_csv(caminho_ou_arquivo, header=None)
        elif caminho_ou_arquivo.lower().endswith(".xls"):
            bruto = pd.read_excel(caminho_ou_arquivo, engine="xlrd", header=None)
        else:
            bruto = pd.read_excel(caminho_ou_arquivo, header=None)
    else:
        nome = caminho_ou_arquivo.name.lower()
        if nome.endswith(".csv"):
            bruto = pd.read_csv(caminho_ou_arquivo, header=None)
        elif nome.endswith(".xls"):
            bruto = pd.read_excel(caminho_ou_arquivo, engine="xlrd", header=None)
        else:
            bruto = pd.read_excel(caminho_ou_arquivo, header=None)

    # A planilha original começa com três linhas de títulos/cabeçalhos.
    # Posições 3 a 5605 (última linha = Brasília/DF) contêm os dados.
    # As 19 colunas são 1 localidade + 6 meios de transporte x 3 grupos.
    df = bruto.iloc[3:5606].copy()
    df.columns = [
        "uf_regiao",

        "Branca/A pé",
        "Branca/Bicicleta",
        "Branca/Motocicleta ou Mototaxi",
        "Branca/Automóvel, taxi ou assemelhados",
        "Branca/Transporte coletivo",
        "Branca/Outros",

        "Preta ou Parda/A pé", 
        "Preta ou Parda/Bicicleta",
        "Preta ou Parda/Motocicleta ou Mototaxi",
        "Preta ou Parda/Automóvel, taxi ou assemelhados",
        "Preta ou Parda/Transporte coletivo", 
        "Preta ou Parda/Outros",

        "Indígena/A pé", 
        "Indígena/Bicicleta",
        "Indígena/Motocicleta ou Mototaxi",
        "Indígena/Automóvel, taxi ou assemelhados",
        "Indígena/Transporte coletivo", 
        "Indígena/Outros"
    ]
    df = df.reset_index(drop=True)

    # todas as colunas a partir da segunda vira numero inves de texto
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # retorna a tabela
    return df

# ==============================================================================
# 3. BARRA LATERAL (SIDEBAR) - CARREGAMENTO E FILTROS
# ==============================================================================
st.sidebar.title("📌 Menu & Filtros")
st.sidebar.subheader("📂 Arquivo de Entrada (Pandas)")
file_transporte = st.sidebar.file_uploader(
    "Upload Tabela 13 (Meios de Transporte):", type=["xls", "xlsx", "csv"]
)

df_transporte = None
try:
    if file_transporte is not None:
        df_transporte = carregar_e_limpar_transporte(file_transporte)
    elif os.path.exists(caminho_transporte_padrao):
        df_transporte = carregar_e_limpar_transporte(caminho_transporte_padrao)
except Exception as e:
    st.sidebar.error(f"Erro ao carregar Tabela 13: {e}")

if df_transporte is None:
    st.warning("⚠️ Aguardando leitura de dados pelo Pandas.")
    st.info(f"""
    Não foi possível carregar automaticamente o arquivo no caminho:

    `{caminho_transporte_padrao}`

    **Solução:** utilize o upload na barra lateral para enviar o Excel ou CSV.
    """)
    st.stop()

# ==============================================================================
# VARIÁVEIS GLOBAIS (DEFINIDAS PARA TODAS AS PÁGINAS)
# ==============================================================================
br_transporte = df_transporte[df_transporte["uf_regiao"] == "Brasil"]

# serve pra pode escolher um dos seis meios.
MEIOS = [
    "A pé", "Bicicleta", "Motocicleta ou Mototaxi",
    "Automóvel, taxi ou assemelhados", "Transporte coletivo", "Outros"
]

st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Selecione a Visualização:",
    ["🏠 Visão Geral", "📊 Meios de Transporte"]
)

st.sidebar.markdown("---")
meio = st.sidebar.selectbox("Meio de transporte:", MEIOS, index=4)

col_branca = f"Branca/{meio}"
col_parda = f"Preta ou Parda/{meio}"
col_indigena = f"Indígena/{meio}"

branca_br = br_transporte[col_branca].values[0] if not br_transporte.empty else float("nan")
parda_br = br_transporte[col_parda].values[0] if not br_transporte.empty else float("nan")
indigena_br = br_transporte[col_indigena].values[0] if not br_transporte.empty else float("nan")

REGIOES = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-oeste"]
st.sidebar.markdown("---")
tipo_visao = st.sidebar.radio(
    "Filtrar recorte:",
    ["Apenas Estados (27 UFs)", "Apenas Regiões e Brasil", "Municípios"]
)

UFs = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba",
    "Pernambuco", "Alagoas", "Sergipe", "Bahia", "Minas Gerais",
    "Espírito Santo", "Rio de Janeiro", "São Paulo", "Paraná",
    "Santa Catarina", "Rio Grande do Sul", "Mato Grosso do Sul",
    "Mato Grosso", "Goiás", "Distrito Federal"
]

if tipo_visao == "Apenas Estados (27 UFs)":
    df_fil = df_transporte[df_transporte["uf_regiao"].isin(UFs)].copy()
elif tipo_visao == "Apenas Regiões e Brasil":
    df_fil = df_transporte[df_transporte["uf_regiao"].isin(REGIOES)].copy()
else:
    df_fil = df_transporte[
        ~df_transporte["uf_regiao"].isin(REGIOES + UFs)
    ].copy()

locais_disp = df_fil["uf_regiao"].tolist()
# Comeca sem municipio pq e muitos pra nao ficar uma tabela gigante
locais_padrao = [] if tipo_visao == "Municípios" else locais_disp
locais_sel = st.sidebar.multiselect(
    "Filtrar UFs / Regiões / Municípios:", locais_disp, default=locais_padrao
)
if locais_sel:
    df_fil = df_fil[df_fil["uf_regiao"].isin(locais_sel)]
elif tipo_visao == "Municípios":
    df_fil = df_fil.iloc[0:0].copy()

# ==============================================================================
# 4. PÁGINA: VISÃO GERAL
# ==============================================================================
if pagina == "🏠 Visão Geral":
    st.title("📊 Painel IBGE - Mulheres e Meios de Transporte")
    st.markdown("Tabela 13, Censo 2022: percentuais tratados via **Pandas**.")
    st.caption(f"Indicadores do Brasil — meio selecionado: {meio}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Mulheres brancas", f"{branca_br:.1f}%")
    col2.metric("Mulheres pretas ou pardas", f"{parda_br:.1f}%")
    col3.metric("Mulheres indígenas", f"{indigena_br:.1f}%")

    st.markdown("---")
    st.subheader("📋 Visualização da Tabela Tratada (Pandas)")
    st.dataframe(df_fil, use_container_width=True)

# ==============================================================================
# 5. PÁGINA: MEIOS DE TRANSPORTE
# ==============================================================================
elif pagina == "📊 Meios de Transporte":
    st.title("🚌 Meios de Transporte para o Trabalho - Mulheres")
    st.caption(f"Meio selecionado: {meio} | Valores em percentual (%)")

    # GRÁFICO 1: e o percentual por local e o brasil de refencia, grafico de barras
    st.subheader("1. Percentual por Localidade vs. Brasil")
    fig_tot = px.bar(
        df_fil.sort_values(col_branca, ascending=True),
        x=col_branca,
        y="uf_regiao",
        orientation="h",
        color=col_branca,
        labels={col_branca: "Percentual (%)", "uf_regiao": "Localidade"},
        text_auto=".1f",
        color_continuous_scale="Blues"
    )
    if not br_transporte.empty:
        fig_tot.add_vline(
            x=branca_br, line_dash="dash", line_color="red",
            annotation_text=f"Brasil: {branca_br:.1f}%"
        )
    st.caption("Gráfico 1: grupo de mulheres brancas. A linha compara com o percentual nacional do mesmo grupo.")
    st.plotly_chart(fig_tot, use_container_width=True)

    # GRÁFICO 2: compara as racas/cor no local selecionado, grafico de colunas
    st.subheader("2. Comparativo por Cor ou Raça")
    df_melt_gen = df_fil.melt(
        id_vars=["uf_regiao"],
        value_vars=[col_branca, col_parda, col_indigena],
        var_name="Grupo",
        value_name="Percentual"
    )
    df_melt_gen["Grupo"] = df_melt_gen["Grupo"].map({
        col_branca: "Branca",
        col_parda: "Preta ou parda",
        col_indigena: "Indígena"
    })
    fig_gen = px.bar(
        df_melt_gen,
        x="uf_regiao", y="Percentual", color="Grupo", barmode="group",
        labels={"Percentual": "Percentual (%)", "uf_regiao": "Localidade"}
    )
    st.plotly_chart(fig_gen, use_container_width=True)

    # GRÁFICO 3: mesma coisa que o de coluna mas com boxplot, pra ver a distribuicao dos valores
    st.subheader("3. Distribuição dos Percentuais por Cor ou Raça (Boxplot)")
    df_melt_raca = df_fil.melt(
        id_vars=["uf_regiao"],
        value_vars=[col_branca, col_parda, col_indigena],
        var_name="Grupo", value_name="Percentual"
    )
    mapa_raca = {
        col_branca: "Branca", col_parda: "Preta ou parda",
        col_indigena: "Indígena"
    }
    df_melt_raca["Grupo"] = df_melt_raca["Grupo"].map(mapa_raca)
    fig_box = px.box(
        df_melt_raca, x="Grupo", y="Percentual", color="Grupo",
        points="all", title="Distribuição entre as Localidades Selecionadas"
    )
    st.plotly_chart(fig_box, use_container_width=True)
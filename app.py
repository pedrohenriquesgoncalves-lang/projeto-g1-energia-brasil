from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Consumo de Energia no Brasil", page_icon="⚡", layout="wide")
sns.set_theme(style="whitegrid")

BASE = Path(__file__).parent
CSV = BASE / "dados" / "simulacao_consumo_energia_brasil.csv"
DB = BASE / "database" / "energia.db"
NUMERICAS = ["consumo_mwh", "demanda_pico", "temperatura_media", "tarifa_media",
             "populacao", "eficiencia_energetica", "emissao_co2"]


@st.cache_data
def carregar():
    DB.parent.mkdir(exist_ok=True)
    engine = create_engine(f"sqlite:///{DB.as_posix()}")
    if not DB.exists():
        bruto = pd.read_csv(CSV, encoding="utf-8-sig", parse_dates=["data"])
        bruto.to_sql("consumo", engine, index=False, if_exists="replace")
    df = pd.read_sql("SELECT * FROM consumo", engine, parse_dates=["data"])
    df["consumo_per_capita"] = df["consumo_mwh"] / df["populacao"]
    df["custo_estimado"] = df["consumo_mwh"] * 1000 * df["tarifa_media"]
    return df


def moeda_milhoes(valor):
    return f"R$ {valor / 1e6:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")


def numero(valor, casas=0):
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


df = carregar()

st.title("⚡ Consumo de Energia no Brasil (2015–2024)")
st.markdown(
    "**Problema:** como o consumo de energia elétrica se distribui entre regiões, estados e setores, "
    "e como ele evolui ao longo do tempo? Este painel permite filtrar a base e acompanhar consumo, "
    "emissões de CO₂ e eficiência energética. A base é uma **simulação** com 4.440 registros mensais."
)

st.sidebar.header("Filtros")
regioes = st.sidebar.multiselect("Região", sorted(df["regiao"].unique()), default=sorted(df["regiao"].unique()))
setores = st.sidebar.multiselect("Setor", sorted(df["setor_consumo"].unique()), default=sorted(df["setor_consumo"].unique()))
niveis = st.sidebar.multiselect("Nível de demanda", ["Baixo", "Médio", "Alto", "Crítico"], default=["Baixo", "Médio", "Alto", "Crítico"])
ano_min, ano_max = int(df["ano"].min()), int(df["ano"].max())
anos = st.sidebar.slider("Período (ano)", ano_min, ano_max, (ano_min, ano_max))

f = df[df["regiao"].isin(regioes) & df["setor_consumo"].isin(setores)
       & df["nivel_demanda"].isin(niveis) & df["ano"].between(*anos)]

if f.empty:
    st.warning("Nenhum registro para os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

st.subheader("Indicadores")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Consumo total", f"{numero(f['consumo_mwh'].sum())} MWh")
c2.metric("Consumo médio por registro", f"{numero(f['consumo_mwh'].mean())} MWh")
c3.metric("Emissão total de CO₂", numero(f["emissao_co2"].sum()))
c4.metric("Eficiência média", numero(f["eficiencia_energetica"].mean(), 1))
c5.metric("Custo estimado", moeda_milhoes(f["custo_estimado"].sum()))
st.caption(f"{numero(len(f))} registros selecionados de {numero(len(df))}.")

aba1, aba2, aba3, aba4, aba5 = st.tabs(["Visão geral", "Análise temporal", "Estados", "Correlação", "Dados"])

with aba1:
    esq, dir_ = st.columns(2)
    por_setor = f.groupby("setor_consumo")["consumo_mwh"].sum().sort_values(ascending=False)
    por_regiao = f.groupby("regiao")["consumo_mwh"].sum().sort_values(ascending=False)
    with esq:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=por_setor.index, y=por_setor.values, ax=ax)
        ax.set_title("Consumo total por setor")
        ax.set_xlabel("Setor")
        ax.set_ylabel("Consumo (MWh)")
        st.pyplot(fig)
    with dir_:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=por_regiao.index, y=por_regiao.values, ax=ax)
        ax.set_title("Consumo total por região")
        ax.set_xlabel("Região")
        ax.set_ylabel("Consumo (MWh)")
        st.pyplot(fig)
    media_regiao = f.groupby("regiao")["consumo_mwh"].mean()
    st.markdown(
        f"**Interpretação:** com os filtros atuais, o setor de maior consumo é **{por_setor.index[0]}** "
        f"({por_setor.iloc[0] / por_setor.sum():.1%} do total) e a região líder é **{por_regiao.index[0]}** "
        f"({por_regiao.iloc[0] / por_regiao.sum():.1%}). O consumo médio por registro varia pouco entre as regiões "
        f"(de {numero(media_regiao.min())} a {numero(media_regiao.max())} MWh), o que indica que a liderança de uma região "
        f"decorre principalmente do número de registros (estados) que ela possui, e não de um consumo individual maior."
    )

with aba2:
    serie = f.groupby("data")["consumo_mwh"].sum()
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(serie.index, serie.values, alpha=0.5, label="Consumo mensal")
    ax.plot(serie.index, serie.rolling(12, min_periods=1).mean(), linewidth=2, label="Média móvel (12 meses)")
    ax.set_title("Evolução mensal do consumo")
    ax.set_xlabel("Data")
    ax.set_ylabel("Consumo (MWh)")
    ax.legend()
    st.pyplot(fig)
    esq, dir_ = st.columns(2)
    anual = f.groupby("ano")["consumo_mwh"].sum()
    mensal = f.groupby("mes")["consumo_mwh"].mean()
    with esq:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=anual.index, y=anual.values, ax=ax, color="#1d4ed8")
        ax.set_title("Consumo total por ano")
        ax.set_xlabel("Ano")
        ax.set_ylabel("Consumo (MWh)")
        st.pyplot(fig)
    with dir_:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.lineplot(x=mensal.index, y=mensal.values, marker="o", ax=ax)
        ax.set_title("Consumo médio por mês do ano")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Consumo médio (MWh)")
        ax.set_xticks(range(1, 13))
        st.pyplot(fig)
    st.markdown(
        f"**Interpretação:** no recorte selecionado, o ano de maior consumo é **{anual.idxmax()}** "
        f"({numero(anual.max())} MWh) e o de menor é **{anual.idxmin()}** ({numero(anual.min())} MWh). "
        f"Na média por mês do calendário, o pico ocorre em **{mensal.idxmax()}** e o menor valor em **{mensal.idxmin()}**. "
        f"A média móvel de 12 meses suaviza as oscilações e mostra a tendência de longo prazo."
    )

with aba3:
    por_uf = f.groupby("uf")["consumo_mwh"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=por_uf.values, y=por_uf.index, ax=ax, color="#0ea5e9")
    ax.set_title("Consumo total por estado")
    ax.set_xlabel("Consumo (MWh)")
    ax.set_ylabel("UF")
    st.pyplot(fig)
    st.markdown(
        f"**Interpretação:** **{por_uf.index[0]}** é o estado de maior consumo ({numero(por_uf.iloc[0])} MWh), "
        f"seguido de **{por_uf.index[1] if len(por_uf) > 1 else '-'}**. Os três maiores estados somam "
        f"{por_uf.head(3).sum() / por_uf.sum():.1%} do consumo filtrado."
    )

with aba4:
    corr = f[NUMERICAS].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1, ax=ax)
    ax.set_title("Matriz de correlação de Pearson")
    st.pyplot(fig)
    pares = corr.where(~pd.DataFrame(
        [[i == j for j in corr.columns] for i in corr.index], index=corr.index, columns=corr.columns)).abs().stack()
    par = pares.idxmax()
    st.markdown(
        f"**Interpretação:** a maior correlação entre variáveis distintas é de **{corr.loc[par]:.2f}** "
        f"({par[0]} × {par[1]}). Valores próximos de 0 indicam ausência de relação linear. "
        f"Na base completa todas as correlações ficam abaixo de 0,05, o que é coerente com dados simulados de forma independente."
    )

with aba5:
    st.subheader("Resumo por região e setor")
    resumo = (f.groupby(["regiao", "setor_consumo"])["consumo_mwh"].agg(["count", "sum", "mean"])
              .round(0).reset_index()
              .rename(columns={"regiao": "Região", "setor_consumo": "Setor", "count": "Registros",
                               "sum": "Consumo total (MWh)", "mean": "Consumo médio (MWh)"}))
    st.dataframe(resumo, width="stretch", hide_index=True)
    st.subheader("Dados filtrados")
    st.dataframe(f.drop(columns=["custo_estimado"]), width="stretch", hide_index=True)
    st.download_button("Baixar dados filtrados (CSV)", f.to_csv(index=False).encode("utf-8-sig"),
                       file_name="consumo_filtrado.csv", mime="text/csv")

st.subheader("Conclusão executiva")
st.markdown(
    "- O consumo total da base é de cerca de **165,7 milhões de MWh** (2015–2024), distribuído de forma equilibrada entre os cinco setores, "
    "com diferença de apenas ~10% entre o maior (Público) e o menor (Residencial).\n"
    "- O **Sudeste concentra 36%** do consumo, mas porque reúne mais registros; o consumo médio por registro é semelhante em todas as regiões.\n"
    "- A série anual teve **queda em 2020** (cerca de −9,5% frente a 2019), recuperação em 2021 e pico em 2022.\n"
    "- Não há correlação linear relevante entre consumo e as demais variáveis, o que limita o poder explicativo da base.\n"
    "- **Recomendação:** priorizar ações de eficiência nos estados e meses de maior consumo, e validar estes achados com dados reais antes de decisões de investimento.\n"
    "- **Limitação:** a base é simulada; os resultados servem para demonstrar a metodologia."
)

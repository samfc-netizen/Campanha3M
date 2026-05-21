
import io
import re
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análise 3M x Norton", layout="wide")

COR_3M = "#D71920"
COR_NORTON = "#0057B8"
COLOR_MAP = {"3M": COR_3M, "NORTON": COR_NORTON}

LOJAS_MAP = {
    "001": "GUARÁ",
    "004": "ADE",
    "006": "GAMA",
    "008": "LUZIÂNIA",
    "009": "ÚNICA",
    "012": "SOFNORTE",
    "013": "CEILÂNDIA",
    "014": "S IA",
    "015": "UNAÍ",
    "016": "AG LINDAS",
    "020": "DAUTO SERVIÇOS",
    "022": "GUARÁ",
    "024": "LUZIÂNIA",
}

PRODUTOS = {
    23110: {"marca": "3M", "grao": "080", "produto_base": "DISCO BLUE 080 152MM 7F 321U 3M"},
    23104: {"marca": "3M", "grao": "120", "produto_base": "DISCO BLUE 120 152MM 7F 321U 3M"},
    23105: {"marca": "3M", "grao": "150", "produto_base": "DISCO BLUE 150 152MM 7F 321U 3M"},
    23125: {"marca": "3M", "grao": "180", "produto_base": "DISCO BLUE 180 152MM 7F 321U 3M"},
    23106: {"marca": "3M", "grao": "220", "produto_base": "DISCO BLUE 220 152MM 7F 321U 3M"},
    23107: {"marca": "3M", "grao": "320", "produto_base": "DISCO BLUE 320 152MM 7F 321U 3M"},
    23108: {"marca": "3M", "grao": "400", "produto_base": "DISCO BLUE 400 152MM 7F 321U 3M"},
    23127: {"marca": "3M", "grao": "500", "produto_base": "DISCO BLUE 500 152MM 7F 321U 3M"},
    23109: {"marca": "3M", "grao": "600", "produto_base": "DISCO BLUE 600 152MM 7F 321U 3M"},
    23123: {"marca": "3M", "grao": "800", "produto_base": "DISCO BLUE 800 152MM 7F 321U 3M"},
    23126: {"marca": "3M", "grao": "040", "produto_base": "DISCO BLUE 040 152MM 7F 321U 3M"},

    10236: {"marca": "NORTON", "grao": "080", "produto_base": "DISCO HOOKIT 080 NORTON"},
    10224: {"marca": "NORTON", "grao": "120", "produto_base": "DISCO HOOKIT 120 NORTON"},
    10226: {"marca": "NORTON", "grao": "150", "produto_base": "DISCO HOOKIT 150 NORTON"},
    10228: {"marca": "NORTON", "grao": "180", "produto_base": "DISCO HOOKIT 180 NORTON"},
    10230: {"marca": "NORTON", "grao": "220", "produto_base": "DISCO HOOKIT 220 NORTON"},
    10232: {"marca": "NORTON", "grao": "320", "produto_base": "DISCO HOOKIT 320 NORTON"},
    10234: {"marca": "NORTON", "grao": "400", "produto_base": "DISCO HOOKIT 400 NORTON"},
    85406: {"marca": "NORTON", "grao": "500", "produto_base": "DISCO HOOKIT 500 NORTON"},
    10237: {"marca": "NORTON", "grao": "600", "produto_base": "DISCO HOOKIT 600 NORTON"},
    10223: {"marca": "NORTON", "grao": "800", "produto_base": "DISCO HOOKIT 800 NORTON"},
}

def br_num(valor, casas=0):
    try:
        if pd.isna(valor):
            valor = 0
        s = f"{float(valor):,.{casas}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return valor

def br_moeda(valor):
    try:
        if pd.isna(valor):
            valor = 0
        s = f"R$ {float(valor):,.2f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return valor

def to_number_br(series):
    return (
        series.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("R$", "", regex=False)
        .str.strip()
        .replace({"": "0", "nan": "0", "None": "0"})
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
    )

def localizar_cabecalho_e_ler(uploaded_file):
    raw = uploaded_file.getvalue()
    erros = []

    for enc in ["cp1252", "latin1", "ISO-8859-1", "utf-8-sig", "utf-8"]:
        try:
            texto = raw.decode(enc)
        except Exception as e:
            erros.append(f"{enc}: erro decode {e}")
            continue

        linhas = texto.splitlines()
        header_idx = None

        for i, linha in enumerate(linhas):
            linha_upper = linha.upper()
            if "CLIENTE" in linha_upper and "CÓD" in linha_upper and "DESCRI" in linha_upper and "VR.TOTAL" in linha_upper:
                header_idx = i
                break

        if header_idx is None:
            erros.append(f"{enc}: cabeçalho não localizado")
            continue

        for sep in [";", ",", "\t"]:
            try:
                df = pd.read_csv(
                    io.StringIO(texto),
                    sep=sep,
                    skiprows=header_idx,
                    header=0,
                    dtype=str,
                    engine="python",
                    on_bad_lines="skip"
                )

                df.columns = [str(c).strip().upper() for c in df.columns]

                if {"CLIENTE", "CÓD", "DESCRIÇÃO", "QTD", "VR.TOTAL"}.issubset(set(df.columns)):
                    return df

                erros.append(f"{enc}/{sep}: colunas encontradas: {list(df.columns)}")
            except Exception as e:
                erros.append(f"{enc}/{sep}: {e}")

    raise ValueError(" | ".join(erros[:8]))

def preparar_dados(df):
    df = df.copy()

    # Remove linhas totalmente vazias e linhas repetidas de cabeçalho
    df = df.dropna(how="all")
    df = df[df["CLIENTE"].astype(str).str.upper().str.strip() != "CLIENTE"]

    df["CODIGO"] = pd.to_numeric(df["CÓD"], errors="coerce").astype("Int64")
    df["QTD_NUM"] = to_number_br(df["QTD"])
    df["UNIT_NUM"] = to_number_br(df["UNIT"]) if "UNIT" in df.columns else 0
    df["VR_TOTAL_NUM"] = to_number_br(df["VR.TOTAL"])
    df["CUSTO_NUM"] = to_number_br(df["CUSTO"]) if "CUSTO" in df.columns else 0

    df["MARCA"] = df["CODIGO"].map(lambda x: PRODUTOS.get(int(x), {}).get("marca") if pd.notna(x) else None)
    df["GRÃO"] = df["CODIGO"].map(lambda x: PRODUTOS.get(int(x), {}).get("grao") if pd.notna(x) else None)
    df["PRODUTO_BASE"] = df["CODIGO"].map(lambda x: PRODUTOS.get(int(x), {}).get("produto_base") if pd.notna(x) else None)

    df = df[df["MARCA"].isin(["3M", "NORTON"])].copy()

    emp_col = "EMP" if "EMP" in df.columns else None
    if emp_col:
        df["LOJA_COD"] = df[emp_col].astype(str).str.extract(r"(\d+)")[0].str.zfill(3)
        df["LOJA"] = df["LOJA_COD"].map(LOJAS_MAP).fillna(df["LOJA_COD"])
        df["LOJA_COMPLETA"] = df["LOJA_COD"] + " - " + df["LOJA"]
    else:
        df["LOJA_COD"] = ""
        df["LOJA"] = "NÃO IDENTIFICADA"
        df["LOJA_COMPLETA"] = "NÃO IDENTIFICADA"

    df["CLIENTE"] = df["CLIENTE"].astype(str).str.strip()
    df["DESCRIÇÃO"] = df["DESCRIÇÃO"].astype(str).str.strip()

    if "DATA" in df.columns:
        df["DATA_REF"] = pd.to_datetime(df["DATA"], dayfirst=True, errors="coerce")
    else:
        df["DATA_REF"] = pd.NaT

    return df

def formatar_tabela(df, dinheiro=None, quantidade=None):
    dinheiro = dinheiro or []
    quantidade = quantidade or []
    out = df.copy()
    for col in dinheiro:
        if col in out.columns:
            out[col] = out[col].apply(br_moeda)
    for col in quantidade:
        if col in out.columns:
            out[col] = out[col].apply(lambda x: br_num(x, 0))
    return out

st.title("Análise de Discos e Lixas — 3M x Norton")

st.markdown(
    """
    Faça upload do CSV exportado do ERP.  
    O sistema compara consumo de **3M** e **Norton**, identifica clientes que compram apenas Norton e mostra a análise por loja, cliente e grão.
    """
)

uploaded = st.file_uploader("Upload do CSV", type=["csv"])

if not uploaded:
    st.info("Envie o CSV para iniciar a análise.")
    st.stop()

try:
    base = localizar_cabecalho_e_ler(uploaded)
    df = preparar_dados(base)
except Exception as e:
    st.error("Não foi possível ler o CSV.")
    st.warning("Detalhes técnicos:")
    st.code(str(e))
    st.stop()

if df.empty:
    st.warning("Nenhum produto 3M ou Norton da lista foi encontrado no arquivo.")
    st.stop()

with st.sidebar:
    st.header("Filtros")

    lojas = sorted(df["LOJA_COMPLETA"].dropna().unique())
    lojas_sel = st.multiselect("Drill de loja", lojas, default=lojas)

    marcas_sel = st.multiselect("Marca", ["3M", "NORTON"], default=["3M", "NORTON"])

    graos = sorted(df["GRÃO"].dropna().unique(), key=lambda x: int(x))
    graos_sel = st.multiselect("Grão", graos, default=graos)

    clientes = sorted(df["CLIENTE"].dropna().unique())
    cliente_busca = st.text_input("Buscar cliente")

df_f = df[
    df["LOJA_COMPLETA"].isin(lojas_sel)
    & df["MARCA"].isin(marcas_sel)
    & df["GRÃO"].isin(graos_sel)
].copy()

if cliente_busca:
    df_f = df_f[df_f["CLIENTE"].str.contains(cliente_busca, case=False, na=False)]

if df_f.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

qtd_3m = df_f.loc[df_f["MARCA"] == "3M", "QTD_NUM"].sum()
qtd_norton = df_f.loc[df_f["MARCA"] == "NORTON", "QTD_NUM"].sum()
fat_3m = df_f.loc[df_f["MARCA"] == "3M", "VR_TOTAL_NUM"].sum()
fat_norton = df_f.loc[df_f["MARCA"] == "NORTON", "VR_TOTAL_NUM"].sum()

clientes_3m = set(df_f.loc[df_f["MARCA"] == "3M", "CLIENTE"].dropna().unique())
clientes_norton = set(df_f.loc[df_f["MARCA"] == "NORTON", "CLIENTE"].dropna().unique())
somente_norton = sorted(clientes_norton - clientes_3m)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Qtd. 3M", br_num(qtd_3m, 0))
c2.metric("Qtd. Norton", br_num(qtd_norton, 0))
c3.metric("Faturamento 3M", br_moeda(fat_3m))
c4.metric("Faturamento Norton", br_moeda(fat_norton))
c5.metric("Clientes só Norton", br_num(len(somente_norton), 0))

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Visão Geral",
    "Clientes só Norton",
    "Ranking Clientes",
    "Cliente x Cliente",
    "Grão x Grão",
    "Drill por Loja"
])

with tab1:
    st.subheader("Análise Norton x 3M")

    resumo = (
        df_f.groupby("MARCA", as_index=False)
        .agg(QTD=("QTD_NUM", "sum"), FATURAMENTO=("VR_TOTAL_NUM", "sum"), CLIENTES=("CLIENTE", "nunique"))
    )

    col1, col2 = st.columns(2)

    fig_qtd = px.bar(
        resumo,
        x="MARCA",
        y="QTD",
        color="MARCA",
        text="QTD",
        color_discrete_map=COLOR_MAP,
        title="Quantidade por marca"
    )
    fig_qtd.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_qtd.update_layout(showlegend=False)
    col1.plotly_chart(fig_qtd, use_container_width=True)

    fig_fat = px.bar(
        resumo,
        x="MARCA",
        y="FATURAMENTO",
        color="MARCA",
        text="FATURAMENTO",
        color_discrete_map=COLOR_MAP,
        title="Faturamento por marca"
    )
    fig_fat.update_traces(texttemplate="R$ %{text:,.2f}", textposition="outside")
    fig_fat.update_layout(showlegend=False)
    col2.plotly_chart(fig_fat, use_container_width=True)

    st.dataframe(
        formatar_tabela(resumo, dinheiro=["FATURAMENTO"], quantidade=["QTD", "CLIENTES"]),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.subheader("Clientes que compram Norton e não compram 3M")

    base_somente_norton = df_f[df_f["CLIENTE"].isin(somente_norton)].copy()

    tabela_somente = (
        base_somente_norton.groupby(["CLIENTE", "LOJA_COMPLETA"], as_index=False)
        .agg(
            QTD_NORTON=("QTD_NUM", "sum"),
            FATURAMENTO_NORTON=("VR_TOTAL_NUM", "sum"),
            ULTIMA_COMPRA=("DATA_REF", "max")
        )
        .sort_values(["QTD_NORTON", "FATURAMENTO_NORTON"], ascending=False)
    )

    tabela_somente["ULTIMA_COMPRA"] = tabela_somente["ULTIMA_COMPRA"].dt.strftime("%d/%m/%Y")

    st.dataframe(
        formatar_tabela(tabela_somente, dinheiro=["FATURAMENTO_NORTON"], quantidade=["QTD_NORTON"]),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("Ranking dos clientes que mais compram")

    ranking = (
        df_f.groupby(["CLIENTE", "MARCA"], as_index=False)
        .agg(QTD=("QTD_NUM", "sum"), FATURAMENTO=("VR_TOTAL_NUM", "sum"))
        .sort_values("QTD", ascending=False)
    )

    col1, col2 = st.columns(2)

    rank_norton = ranking[ranking["MARCA"] == "NORTON"].head(20)
    fig_norton = px.bar(
        rank_norton,
        x="QTD",
        y="CLIENTE",
        orientation="h",
        color="MARCA",
        color_discrete_map=COLOR_MAP,
        title="Top clientes Norton"
    )
    fig_norton.update_layout(yaxis={"categoryorder": "total ascending"})
    col1.plotly_chart(fig_norton, use_container_width=True)

    rank_3m = ranking[ranking["MARCA"] == "3M"].head(20)
    fig_3m = px.bar(
        rank_3m,
        x="QTD",
        y="CLIENTE",
        orientation="h",
        color="MARCA",
        color_discrete_map=COLOR_MAP,
        title="Top clientes 3M"
    )
    fig_3m.update_layout(yaxis={"categoryorder": "total ascending"})
    col2.plotly_chart(fig_3m, use_container_width=True)

    st.dataframe(
        formatar_tabela(ranking, dinheiro=["FATURAMENTO"], quantidade=["QTD"]),
        use_container_width=True,
        hide_index=True
    )


with tab4:
    st.subheader("Compras por cliente — Norton x 3M")

    cliente_marca = (
        df_f.groupby(["CLIENTE", "MARCA"], as_index=False)
        .agg(QTD=("QTD_NUM", "sum"), FATURAMENTO=("VR_TOTAL_NUM", "sum"))
    )

    qtd_pivot = cliente_marca.pivot_table(
        index="CLIENTE",
        columns="MARCA",
        values="QTD",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    fat_pivot = cliente_marca.pivot_table(
        index="CLIENTE",
        columns="MARCA",
        values="FATURAMENTO",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    for col in ["3M", "NORTON"]:
        if col not in qtd_pivot.columns:
            qtd_pivot[col] = 0
        if col not in fat_pivot.columns:
            fat_pivot[col] = 0

    cliente_comp = qtd_pivot[["CLIENTE", "3M", "NORTON"]].rename(columns={
        "3M": "QTD_3M",
        "NORTON": "QTD_NORTON"
    })

    cliente_comp = cliente_comp.merge(
        fat_pivot[["CLIENTE", "3M", "NORTON"]].rename(columns={
            "3M": "FAT_3M",
            "NORTON": "FAT_NORTON"
        }),
        on="CLIENTE",
        how="left"
    )

    cliente_comp["QTD_TOTAL"] = cliente_comp["QTD_3M"] + cliente_comp["QTD_NORTON"]
    cliente_comp["FAT_TOTAL"] = cliente_comp["FAT_3M"] + cliente_comp["FAT_NORTON"]
    cliente_comp["DIF_QTD_NORTON_MENOS_3M"] = cliente_comp["QTD_NORTON"] - cliente_comp["QTD_3M"]
    cliente_comp["DIF_FAT_NORTON_MENOS_3M"] = cliente_comp["FAT_NORTON"] - cliente_comp["FAT_3M"]

    cliente_comp["%_QTD_3M"] = cliente_comp.apply(
        lambda r: (r["QTD_3M"] / r["QTD_TOTAL"] * 100) if r["QTD_TOTAL"] else 0,
        axis=1
    )
    cliente_comp["%_QTD_NORTON"] = cliente_comp.apply(
        lambda r: (r["QTD_NORTON"] / r["QTD_TOTAL"] * 100) if r["QTD_TOTAL"] else 0,
        axis=1
    )

    def classificar_cliente(row):
        if row["QTD_NORTON"] > 0 and row["QTD_3M"] == 0:
            return "Só Norton"
        if row["QTD_3M"] > 0 and row["QTD_NORTON"] == 0:
            return "Só 3M"
        if row["QTD_3M"] > 0 and row["QTD_NORTON"] > 0:
            return "Misto"
        return "Sem classificação"

    cliente_comp["PERFIL"] = cliente_comp.apply(classificar_cliente, axis=1)

    cliente_comp = cliente_comp.sort_values(
        ["QTD_NORTON", "FAT_NORTON", "QTD_TOTAL"],
        ascending=False
    )

    st.markdown("**Tabela comparativa por cliente**")
    tabela_cliente_comp = cliente_comp.copy()
    tabela_cliente_comp["%_QTD_3M"] = tabela_cliente_comp["%_QTD_3M"].apply(lambda x: f"{x:.1f}%".replace(".", ","))
    tabela_cliente_comp["%_QTD_NORTON"] = tabela_cliente_comp["%_QTD_NORTON"].apply(lambda x: f"{x:.1f}%".replace(".", ","))

    st.dataframe(
        formatar_tabela(
            tabela_cliente_comp,
            dinheiro=["FAT_3M", "FAT_NORTON", "FAT_TOTAL", "DIF_FAT_NORTON_MENOS_3M"],
            quantidade=["QTD_3M", "QTD_NORTON", "QTD_TOTAL", "DIF_QTD_NORTON_MENOS_3M"]
        ),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("**Top clientes com maior presença Norton**")
    top_cliente_norton = cliente_comp.sort_values(["QTD_NORTON", "FAT_NORTON"], ascending=False).head(25)

    fig_cliente_comp = px.bar(
        top_cliente_norton,
        x="CLIENTE",
        y=["QTD_NORTON", "QTD_3M"],
        barmode="group",
        title="Mesmo cliente: Norton x 3M por quantidade",
        labels={"value": "Quantidade", "variable": "Marca"}
    )
    fig_cliente_comp.for_each_trace(
        lambda t: t.update(
            marker_color=COR_NORTON if t.name == "QTD_NORTON" else COR_3M,
            name="Norton" if t.name == "QTD_NORTON" else "3M"
        )
    )
    st.plotly_chart(fig_cliente_comp, use_container_width=True)

    cliente_drill = st.selectbox(
        "Drill por cliente",
        sorted(df_f["CLIENTE"].dropna().unique()),
        key="cliente_drill_comp"
    )

    df_cliente = df_f[df_f["CLIENTE"] == cliente_drill]

    resumo_cliente = (
        df_cliente.groupby(["MARCA", "GRÃO", "PRODUTO_BASE"], as_index=False)
        .agg(QTD=("QTD_NUM", "sum"), FATURAMENTO=("VR_TOTAL_NUM", "sum"))
        .sort_values(["MARCA", "GRÃO"])
    )

    fig_cliente_grao = px.bar(
        resumo_cliente,
        x="GRÃO",
        y="QTD",
        color="MARCA",
        barmode="group",
        color_discrete_map=COLOR_MAP,
        title=f"Produtos comprados por {cliente_drill}"
    )
    st.plotly_chart(fig_cliente_grao, use_container_width=True)

    st.dataframe(
        formatar_tabela(resumo_cliente, dinheiro=["FATURAMENTO"], quantidade=["QTD"]),
        use_container_width=True,
        hide_index=True
    )


with tab5:
    st.subheader("Comparativo Grão x Grão")


    mapa_graos = []
    for grao in sorted({v["grao"] for v in PRODUTOS.values()}, key=lambda x: int(x)):
        norton = [v["produto_base"] for v in PRODUTOS.values() if v["marca"] == "NORTON" and v["grao"] == grao]
        m3 = [v["produto_base"] for v in PRODUTOS.values() if v["marca"] == "3M" and v["grao"] == grao]
        mapa_graos.append({
            "GRÃO": grao,
            "COMPARATIVO": f"{norton[0] if norton else '-'} x {m3[0] if m3 else '-'}",
            "NORTON": norton[0] if norton else "-",
            "3M": m3[0] if m3 else "-"
        })

    st.dataframe(pd.DataFrame(mapa_graos), use_container_width=True, hide_index=True)

    grao_resumo = (
        df_f.groupby(["GRÃO", "MARCA"], as_index=False)
        .agg(QTD=("QTD_NUM", "sum"), FATURAMENTO=("VR_TOTAL_NUM", "sum"))
    )

    fig_grao = px.bar(
        grao_resumo,
        x="GRÃO",
        y="QTD",
        color="MARCA",
        barmode="group",
        color_discrete_map=COLOR_MAP,
        title="Quantidade por grão — Norton x 3M"
    )
    st.plotly_chart(fig_grao, use_container_width=True)

    qtd_grao = grao_resumo.pivot_table(
        index="GRÃO",
        columns="MARCA",
        values="QTD",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    fat_grao = grao_resumo.pivot_table(
        index="GRÃO",
        columns="MARCA",
        values="FATURAMENTO",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    for col in ["3M", "NORTON"]:
        if col not in qtd_grao.columns:
            qtd_grao[col] = 0
        if col not in fat_grao.columns:
            fat_grao[col] = 0

    comp_grao = qtd_grao[["GRÃO", "3M", "NORTON"]].rename(columns={
        "3M": "QTD_3M",
        "NORTON": "QTD_NORTON"
    })

    comp_grao = comp_grao.merge(
        fat_grao[["GRÃO", "3M", "NORTON"]].rename(columns={
            "3M": "FAT_3M",
            "NORTON": "FAT_NORTON"
        }),
        on="GRÃO",
        how="left"
    )

    comp_grao["DIF_QTD_NORTON_MENOS_3M"] = comp_grao["QTD_NORTON"] - comp_grao["QTD_3M"]
    comp_grao["DIF_FAT_NORTON_MENOS_3M"] = comp_grao["FAT_NORTON"] - comp_grao["FAT_3M"]

    comp_grao["QTD_TOTAL"] = comp_grao["QTD_3M"] + comp_grao["QTD_NORTON"]
    comp_grao["FAT_TOTAL"] = comp_grao["FAT_3M"] + comp_grao["FAT_NORTON"]

    comp_grao["%_QTD_3M"] = comp_grao.apply(
        lambda r: (r["QTD_3M"] / r["QTD_TOTAL"] * 100) if r["QTD_TOTAL"] else 0,
        axis=1
    )
    comp_grao["%_QTD_NORTON"] = comp_grao.apply(
        lambda r: (r["QTD_NORTON"] / r["QTD_TOTAL"] * 100) if r["QTD_TOTAL"] else 0,
        axis=1
    )

    comp_grao["MARCA_DOMINANTE_QTD"] = comp_grao.apply(
        lambda r: "Norton" if r["QTD_NORTON"] > r["QTD_3M"] else ("3M" if r["QTD_3M"] > r["QTD_NORTON"] else "Empate"),
        axis=1
    )

    comp_grao = comp_grao.sort_values("GRÃO", key=lambda s: s.astype(int))

    fig_grao_fat = px.bar(
        comp_grao,
        x="GRÃO",
        y=["FAT_NORTON", "FAT_3M"],
        barmode="group",
        title="Faturamento por grão — Norton x 3M",
        labels={"value": "Faturamento", "variable": "Marca"}
    )
    fig_grao_fat.for_each_trace(
        lambda t: t.update(
            marker_color=COR_NORTON if t.name == "FAT_NORTON" else COR_3M,
            name="Norton" if t.name == "FAT_NORTON" else "3M"
        )
    )
    st.plotly_chart(fig_grao_fat, use_container_width=True)

    tabela_comp_grao = comp_grao.copy()
    tabela_comp_grao["%_QTD_3M"] = tabela_comp_grao["%_QTD_3M"].apply(lambda x: f"{x:.1f}%".replace(".", ","))
    tabela_comp_grao["%_QTD_NORTON"] = tabela_comp_grao["%_QTD_NORTON"].apply(lambda x: f"{x:.1f}%".replace(".", ","))

    st.dataframe(
        formatar_tabela(
            tabela_comp_grao,
            dinheiro=["FAT_3M", "FAT_NORTON", "FAT_TOTAL", "DIF_FAT_NORTON_MENOS_3M"],
            quantidade=["QTD_3M", "QTD_NORTON", "QTD_TOTAL", "DIF_QTD_NORTON_MENOS_3M"]
        ),
        use_container_width=True,
        hide_index=True
    )

with tab6:
    st.subheader("Drill por Loja — Norton x 3M")

    loja_drill = st.selectbox("Selecione uma loja para detalhar", sorted(df_f["LOJA_COMPLETA"].unique()))

    df_loja = df_f[df_f["LOJA_COMPLETA"] == loja_drill]

    resumo_loja = (
        df_loja.groupby("MARCA", as_index=False)
        .agg(QTD=("QTD_NUM", "sum"), FATURAMENTO=("VR_TOTAL_NUM", "sum"), CLIENTES=("CLIENTE", "nunique"))
    )

    col1, col2 = st.columns(2)

    fig_loja_qtd = px.pie(
        resumo_loja,
        names="MARCA",
        values="QTD",
        color="MARCA",
        color_discrete_map=COLOR_MAP,
        title=f"Participação por quantidade — {loja_drill}"
    )
    col1.plotly_chart(fig_loja_qtd, use_container_width=True)

    fig_loja_fat = px.bar(
        resumo_loja,
        x="MARCA",
        y="FATURAMENTO",
        color="MARCA",
        color_discrete_map=COLOR_MAP,
        title=f"Faturamento por marca — {loja_drill}"
    )
    fig_loja_fat.update_layout(showlegend=False)
    col2.plotly_chart(fig_loja_fat, use_container_width=True)

    st.dataframe(
        formatar_tabela(resumo_loja, dinheiro=["FATURAMENTO"], quantidade=["QTD", "CLIENTES"]),
        use_container_width=True,
        hide_index=True
    )

    detalhe_loja = (
        df_loja.groupby(["CLIENTE", "MARCA", "GRÃO", "PRODUTO_BASE"], as_index=False)
        .agg(QTD=("QTD_NUM", "sum"), FATURAMENTO=("VR_TOTAL_NUM", "sum"))
        .sort_values(["MARCA", "QTD"], ascending=[True, False])
    )

    st.dataframe(
        formatar_tabela(detalhe_loja, dinheiro=["FATURAMENTO"], quantidade=["QTD"]),
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.subheader("Base tratada")

cols_base = ["DATA", "LOJA_COMPLETA", "CLIENTE", "CPF/CNPJ", "CODIGO", "DESCRIÇÃO", "MARCA", "GRÃO", "QTD_NUM", "UNIT_NUM", "VR_TOTAL_NUM", "CUSTO_NUM"]
cols_base = [c for c in cols_base if c in df_f.columns]

base_view = df_f[cols_base].rename(columns={
    "QTD_NUM": "QTD",
    "UNIT_NUM": "UNIT",
    "VR_TOTAL_NUM": "VR.TOTAL",
    "CUSTO_NUM": "CUSTO"
})

st.dataframe(
    formatar_tabela(base_view, dinheiro=["UNIT", "VR.TOTAL", "CUSTO"], quantidade=["QTD"]),
    use_container_width=True,
    hide_index=True
)

csv_export = df_f.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    "Baixar base tratada em CSV",
    data=csv_export,
    file_name="base_tratada_3m_vs_norton.csv",
    mime="text/csv"
)

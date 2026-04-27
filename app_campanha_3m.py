import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime
from io import StringIO, BytesIO
import csv

st.set_page_config(page_title="Campanha 3M - Metas e Premiação", layout="wide")

# =========================
# CONFIGURAÇÕES FIXAS
# =========================
LOJAS = {
    "1": "GUARÁ",
    "4": "ADE",
    "6": "GAMA",
    "8": "LUZIÂNIA",
    "9": "ÚNICA",
    "12": "SOFNORTE",
    "13": "CEILÂNDIA",
    "14": "S IA",
    "15": "UNAÍ",
    "16": "AG LINDAS",
    "20": "DAUTO SERVIÇOS",
    "22": "GUARÁ",
    "24": "LUZIÂNIA",
}

VENDEDORES = {
    "999":"ADMINISTRAÇÃO CITEL","182":"ADRIANA","91":"AILTON CAVALCANTE","47":"ALESSANDRA","60":"ALEXANDRA","52":"ALEXANDRE",
    "86":"AMANDA","142":"ANA GABRIELA LIMA LINHARES","74":"ANA PAULA","80":"ANDERSON","187":"ANDERSON DOS REIS DE OLIVEIRA",
    "103":"ANTONIO PEREIRA","98":"ARIGLEICE","997":"ATENDIMENTO","16":"AYSLAN","2":"BERNARDO","11":"BRUNO","179":"CAIO CRISTIANO",
    "69":"CAIQUE","189":"CAMILA WILLIANE","36":"CARLOS","190":"CARLOS RODRIGUES DA SILVA","118":"CARNEIRINHO",
    "126":"CESAR OLIVIEIRA DE ARAUJO","192":"CIDA","144":"CINTIA DA SILVA CARLOS","46":"CLAUDMIRO","122":"CLOVIS JUNIO",
    "73":"COMPRADOR FORNECEDOR","72":"COMPRADOR LOJAS","130":"COMPRAS","70":"CONCESSIONARIAS","108":"CRISLANY DA SILVA",
    "64":"CUSTODIO","107":"DAIANA PORTELA","43":"DAMIÃO","42":"DANIEL","17":"DAYANA","56":"DENIS","61":"DIEGO",
    "114":"DIEGO CARNAUBA","137":"DIVINA ALVES DE OLIVEIRA","30":"DOUGLAS","50":"EDELSON","12":"EDSON","151":"EDSON PEREIRA DA SILVA",
    "4":"EDUARDO","176":"EDUARDO DE JESUS BALDUINO","90":"ELEILTON","76":"ELIANA","82":"ELIAS","5":"ELINE","67":"ERIKA",
    "225":"ERIKA ALVES DO NASCIMENTO","111":"ERLANE PANUCE","22":"ESTEFESON","45":"ESTERFFSON","96":"EVANDRO","23":"EXTERNO4",
    "13":"EXTERNOADE","19":"FABIANA","99":"FABIO","145":"FABRICIA","185":"FELIPE OLIVEIRA PONTE","175":"FILIPE DE LIMA CASSIMIRO",
    "200":"FLÁVIO REPRESENTANTE","102":"GABRIEL TEIXEIRA DA ROCHA","28":"GABRIELA","171":"GABRIELLY APARECIDA DE JESUS",
    "31":"GEOVANE","59":"GIAN","68":"GIVANILDO","88":"GLEISON","104":"GUSTAVO","224":"GUSTAVO MOURA DE OLIVEIRA",
    "29":"HELTON","149":"HERSON PEREIRA DA SILVA","18":"HUGO","100":"IDALICE","116":"IGOR PEIXOTO COSTA","95":"INGRIDY",
    "41":"ISMAEL","27":"IVAN","37":"JANAINA","26":"JANUARIO","25":"JEFFERSON","84":"JEICY AZEVEDO","21":"JESSICA",
    "53":"JOÃO FELIX MORAES SANTOS","1":"JOCELIA","51":"JOHN","186":"JOHN LENNON FERREIRA P BUENO","78":"JONAS",
    "153":"JORGE LUIZ DE ALMEIDA","62":"JOSE ANTONIO","63":"JOSE SILVA","83":"JUCERLANDIO","152":"JUNIO ALVES DE ALMEIDA",
    "38":"JUNIOR LIMA","140":"KAREN NAYARA BORGES","127":"KARLA CRISTYNA ALVES FIGUEIRED","210":"KAROL MARKETING",
    "196":"KASSIANO MARCUS ALVES SILVA","207":"KETILE SABRINE","206":"LAURA LISBOA","199":"LEANDRO LUIZ NUNES","81":"LEONARDO",
    "180":"LETICIA ALMEIDA","32":"LIDER ADE","0":"LIMPEZA DE ACESSO","109":"LIVIA DE SOUZA","173":"LÍVIA FRANÇA V. DO E. SANTO",
    "113":"LORRANE DE BRITO","184":"LOUISE REGINA ALVES","35":"LUANA","66":"LUCIANA","89":"LUCIANO","146":"LUCIMEIRE ROSA RIBEIRO",
    "8":"LUIS FERNANDO","44":"LUIS JUNIO","101":"LUIS PINHEIRO RODRIGUES","150":"LUZIBERTO GOMES DA SILVA","77":"MARCELO",
    "156":"MARCELO DA CONCEIÇÃO FERREIRA","97":"MARCIA","181":"MARCIO KELER BITTENCORT VENIS","14":"MARCOS","155":"MARI",
    "193":"MARIA ALICE","170":"MARIA LUISA","143":"MARIA THAINARA L. DA SILVA","209":"MARIA WITHALINA CUNHA DE SOUZA",
    "208":"MARIO DE MOURA SANTANA","131":"MARTILIANA MERIAM LOPES CARDOS","178":"MATEUS","154":"MATHEUS","57":"MAURICIO",
    "20":"MAYARA","79":"MESSIAS","147":"MICAELE DA CONCEIÇAO SILVA","65":"MICHAEL ALVES FERNANDES","198":"MICHELLY DIAS",
    "174":"MIRIÃ LOBATO RODRIGUES","183":"NADINE DE OLIVEIRA MORAIS","117":"NAGILA DA SILVA","9":"NARA","55":"NARGILA",
    "191":"NATHAN DE LIMA SOUSA","75":"NEUTON","128":"NURES GOMES BATISTA","71":"OFICINAS","132":"PAMELA GONÇALVES ROSA",
    "93":"PATRICIA","33":"PAULINHO","115":"PAULO","7":"PEDRO","48":"PEDRO PAULO","197":"POLIANA LORRANE DE AMORIM",
    "123":"PRICILA PAULA DOS SANTOS","998":"PROGRAMAÇÃO","129":"RAFAEL DA SILVA PEREIRA DIAS","120":"RAFAELLA DOS REIS DANTAS",
    "172":"RAIMUNDO AFONSO VIEIRA","139":"RAMOM RODRIGUES DOS SANTOS","39":"RAONIREIS","136":"REGINALDO MARTINS DE ANDRADE",
    "15":"REPRESENTANTE","106":"RICARDO","54":"ROBSON","58":"ROBSON SOARES","24":"ROGERIO","121":"ROMULO COSTA DE ARAUJO JUNIOR",
    "205":"RONAN PARACATU","124":"SAMARA NERYS GUEDES NEVES","135":"SAMUEL DA COSTA F. CARVALHO","148":"SARA LUCIA DE SOUZA",
    "211":"SHEILA MIRANDA","6":"SUZANA","112":"SUZANE DIAS","105":"TARCISIO","AUT":"TAREFA AUTOMÁTICA","195":"UILIAN ALMEIDA",
    "194":"UILIAN VENDAS EXTERNAS","119":"VALDO RODRIGUES","141":"VANDERLEI RIBEIRO","94":"VANESSA KOBELUS","220":"VENDA DE PEÇAS",
    "222":"VENDAS AGREGADAS","995":"VENDEDOR","3":"VICTOR DAMASCENO","40":"VITOR","92":"WAGNER","133":"WALBER",
    "223":"WALBER TAVARES DA CONCEIÇÃO","49":"WASHINGTON","110":"WELBER NAYON","10":"WELLINGTON","85":"WEMERSON",
    "125":"WENDERSON PEREIRA JESUS","34":"WESLEY","87":"WESLLEY","138":"WILLIAM ASSIS FERREIRA DA SILV","212":"YASMIN",
    "134":"YSA ARAUJO","227":"WHALISSON","228":"LUCAS","229":"FRED","230":"SÔNIA","231":"EDIJANE","233":"MARCELO MENEZES",
    "232":"JESSICA GUIMARÃES","234":"MARCOS AURÉLIO","236":"DANIEL","237":"ANTÔNIO","239":"BRUNO","240":"MICHEL","238":"BIANCA",
    "510":"MARCELO","241":"PRISCILA","242":"CRISTIANO","243":"HERICKA","245":"JOÃO PEDRO","226":"MARIA FÉLIX",
    "244":"NATHALIA PEREIRA DA SILVA","246":"VITORIA APARECIDA","247":"TATIELE BRITO","248":"RAFAELA XAVIER"
}

METAS_MARCO = {
    "LUZIÂNIA": 25287.99, "UNAÍ": 11757.97, "ADE": 15435.57, "GAMA": 10813.13,
    "AG LINDAS": 4540.99, "SOFNORTE": 12049.47, "GUARÁ": 12062.68,
    "CEILÂNDIA": 19627.84, "S IA": 16868.99,
}

METAS_ABRIL = {
    "LUZIÂNIA": 31798.89, "UNAÍ": 15114.80, "ADE": 21237.80, "GAMA": 9754.15,
    "AG LINDAS": 4091.91, "SOFNORTE": 11114.73, "GUARÁ": 17030.94,
    "CEILÂNDIA": 22379.31, "S IA": 18927.89,
}

PREMIOS = [
    (1, "TV SMART 50", "01 TV para o gerente da loja 1ª colocada e 01 TV para o vendedor que mais vendeu"),
    (2, "CAIXA DE SOM BOOMBOX 200W AIWA", "2º colocado"),
    (3, "CELULAR SAMSUNG GALAXY A7", "3º colocado"),
    (4, "AIR FRYER MUNDIAL 4L", "4º colocado"),
    (5, "TÊNIS NIKE - VOUCHER", "5º colocado"),
    (6, "PARAFUSADEIRA", "6º colocado"),
    (7, "APARADOR DE CABELO PHILIPS", "7º colocado"),
]

LOJAS_CAMPANHA = list(METAS_MARCO.keys())

# =========================
# FUNÇÕES AUXILIARES
# =========================
def brl(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def pct(v):
    try:
        return f"{float(v):.1f}%".replace(".", ",")
    except Exception:
        return "0,0%"

def normalize_code(x):
    if pd.isna(x):
        return ""
    s = str(x).strip().replace(".0", "")
    if s.isdigit():
        return str(int(s))
    return s.upper()

def parse_num(series):
    s = series.astype(str).str.strip()
    s = s.str.replace("R$", "", regex=False).str.replace(" ", "", regex=False)
    s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce").fillna(0)

def find_header_line(text):
    for i, line in enumerate(text.splitlines()):
        upper = line.upper()
        if "CLIENTE" in upper and "VR.TOTAL" in upper and "EMP" in upper and "VEN" in upper:
            return i
    return 0

def read_autcom_csv(uploaded_file):
    raw = uploaded_file.read()
    for enc in ["latin1", "cp1252", "utf-8"]:
        try:
            text = raw.decode(enc)
            break
        except Exception:
            continue
    else:
        text = raw.decode("latin1", errors="ignore")

    header_line = find_header_line(text)
    data_text = "\n".join(text.splitlines()[header_line:])
    df = pd.read_csv(StringIO(data_text), sep=";", dtype=str, engine="python")

    # Remove colunas vazias geradas pelo relatório
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed")]
    df.columns = [str(c).strip().upper() for c in df.columns]

    # Normaliza nomes com possíveis problemas de acentuação
    rename = {}
    for c in df.columns:
        c2 = c.replace("Nº", "N").replace("N°", "N").replace("NM-:", "N")
        c2 = c2.replace("CÓD", "COD").replace("CM-SD", "COD")
        c2 = c2.replace("DESCRIÇÃO", "DESCRICAO").replace("DESCRIM-GM-CO", "DESCRICAO")
        c2 = c2.replace("%MAR", "%MAR")
        rename[c] = c2
    df = df.rename(columns=rename)

    # Garante nomes principais
    aliases = {
        "VR.TOTAL": ["VR.TOTAL", "VR TOTAL", "VALOR TOTAL"],
        "DATA": ["DATA"],
        "EMP": ["EMP"],
        "VEN": ["VEN"],
        "QTD": ["QTD"],
        "UNIT": ["UNIT"],
        "CUSTO": ["CUSTO"],
        "COD": ["COD", "CÓD"],
        "DESCRICAO": ["DESCRICAO", "DESCRIÇÃO"],
    }
    for final, opts in aliases.items():
        if final not in df.columns:
            for opt in opts:
                if opt in df.columns:
                    df = df.rename(columns={opt: final})
                    break

    required = ["DATA", "EMP", "VEN", "VR.TOTAL"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias não encontradas: {missing}. Verifique se o CSV é o relatório Movimento de Clientes.")

    df = df[df["DATA"].notna()].copy()
    df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True, errors="coerce")
    df = df[df["DATA"].notna()].copy()

    df["EMP_COD"] = df["EMP"].apply(normalize_code)
    df["LOJA"] = df["EMP_COD"].map(LOJAS).fillna("EMP " + df["EMP_COD"].astype(str))
    df["VEN_COD"] = df["VEN"].apply(normalize_code)
    df["VENDEDOR"] = df["VEN_COD"].map(VENDEDORES).fillna("VEN " + df["VEN_COD"].astype(str))
    df["VR.TOTAL"] = parse_num(df["VR.TOTAL"])
    for col in ["QTD", "UNIT", "CUSTO", "%MAR"]:
        if col in df.columns:
            df[col] = parse_num(df[col])
    df["MES"] = df["DATA"].dt.month
    df["ANO"] = df["DATA"].dt.year
    return df

def make_excel(dfs):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in dfs.items():
            safe = name[:31]
            df.to_excel(writer, sheet_name=safe, index=False)
    output.seek(0)
    return output

# =========================
# INTERFACE
# =========================
st.title("Campanha 3M - Acompanhamento de Metas e Premiação")
st.caption("Upload do CSV do Movimento de Clientes. O app identifica loja pelo campo EMP e vendedor pelo campo VEN.")

uploaded = st.file_uploader("Anexe o CSV", type=["csv", "txt"])

with st.sidebar:
    st.header("Parâmetros")
    crescimento = st.number_input("Meta de crescimento (%)", min_value=0.0, max_value=100.0, value=15.0, step=0.5) / 100
    data_fim = st.date_input("Fim da campanha", value=date(2026, 4, 30))
    considerar_lojas = st.multiselect("Lojas da campanha", options=LOJAS_CAMPANHA, default=LOJAS_CAMPANHA)

if not uploaded:
    st.info("Anexe o arquivo CSV para gerar a análise.")
    st.stop()

try:
    df = read_autcom_csv(uploaded)
except Exception as e:
    st.error(f"Erro ao ler o CSV: {e}")
    st.stop()

# Usa o ano do próprio CSV como referência de apuração
anos = sorted(df["ANO"].dropna().unique().tolist())
ano_padrao = int(max(anos)) if anos else 2026
ano_sel = st.sidebar.selectbox("Ano de apuração", options=anos if anos else [ano_padrao], index=(len(anos)-1 if anos else 0))

# Data de referência: maior data do CSV, limitada ao fim da campanha no mesmo ano escolhido
max_data_csv = df[df["ANO"] == ano_sel]["DATA"].max().date()
data_ref = st.sidebar.date_input("Data de referência para projeção", value=max_data_csv)
dias_restantes = max((data_fim - data_ref).days, 0)

base = df[(df["ANO"] == ano_sel) & (df["MES"].isin([3, 4])) & (df["LOJA"].isin(considerar_lojas))].copy()

# Metas por loja
metas = pd.DataFrame({
    "LOJA": LOJAS_CAMPANHA,
    "META_MARCO": [METAS_MARCO[l] for l in LOJAS_CAMPANHA],
    "META_ABRIL": [METAS_ABRIL[l] for l in LOJAS_CAMPANHA],
})
metas["BASE_BIMESTRE"] = metas["META_MARCO"] + metas["META_ABRIL"]
metas["META_15"] = metas["BASE_BIMESTRE"] * (1 + crescimento)
metas = metas[metas["LOJA"].isin(considerar_lojas)].copy()

real = base.pivot_table(index="LOJA", columns="MES", values="VR.TOTAL", aggfunc="sum", fill_value=0).reset_index()
real = real.rename(columns={3: "REAL_MARCO", 4: "REAL_ABRIL"})
for c in ["REAL_MARCO", "REAL_ABRIL"]:
    if c not in real.columns:
        real[c] = 0.0

resumo = metas.merge(real, on="LOJA", how="left").fillna(0)
resumo["REAL_BIMESTRE"] = resumo["REAL_MARCO"] + resumo["REAL_ABRIL"]
resumo["FALTA_META"] = (resumo["META_15"] - resumo["REAL_BIMESTRE"]).clip(lower=0)
resumo["%_ATINGIMENTO"] = np.where(resumo["META_15"] > 0, resumo["REAL_BIMESTRE"] / resumo["META_15"] * 100, 0)
resumo["VENDA_DIA_NECESSARIA"] = np.where(dias_restantes > 0, resumo["FALTA_META"] / dias_restantes, resumo["FALTA_META"])
resumo["STATUS"] = np.where(resumo["REAL_BIMESTRE"] >= resumo["META_15"], "✅ Bateu", "❌ Não bateu")
resumo = resumo.sort_values(["%_ATINGIMENTO", "REAL_BIMESTRE"], ascending=False).reset_index(drop=True)
resumo["RANKING_LOJA"] = resumo.index + 1

# Resumo geral
geral = pd.DataFrame([{ 
    "LOJA": "TOTAL GERAL",
    "META_MARCO": resumo["META_MARCO"].sum(),
    "META_ABRIL": resumo["META_ABRIL"].sum(),
    "BASE_BIMESTRE": resumo["BASE_BIMESTRE"].sum(),
    "META_15": resumo["META_15"].sum(),
    "REAL_MARCO": resumo["REAL_MARCO"].sum(),
    "REAL_ABRIL": resumo["REAL_ABRIL"].sum(),
    "REAL_BIMESTRE": resumo["REAL_BIMESTRE"].sum(),
}])
geral["FALTA_META"] = (geral["META_15"] - geral["REAL_BIMESTRE"]).clip(lower=0)
geral["%_ATINGIMENTO"] = geral["REAL_BIMESTRE"] / geral["META_15"] * 100
geral["VENDA_DIA_NECESSARIA"] = geral["FALTA_META"] / dias_restantes if dias_restantes > 0 else geral["FALTA_META"]
geral["STATUS"] = np.where(geral["REAL_BIMESTRE"] >= geral["META_15"], "✅ Bateu", "❌ Não bateu")

# Rankings vendedores
rank_vend = base.groupby(["VEN_COD", "VENDEDOR"], as_index=False)["VR.TOTAL"].sum()
rank_vend = rank_vend.sort_values("VR.TOTAL", ascending=False).reset_index(drop=True)
rank_vend["RANKING"] = rank_vend.index + 1

rank_vend_loja = base.groupby(["LOJA", "VEN_COD", "VENDEDOR"], as_index=False)["VR.TOTAL"].sum()
rank_vend_loja = rank_vend_loja.sort_values(["LOJA", "VR.TOTAL"], ascending=[True, False])
rank_vend_loja["RANKING_LOJA"] = rank_vend_loja.groupby("LOJA")["VR.TOTAL"].rank(method="first", ascending=False).astype(int)

# Crescimento do bimestre: realizado atual vs base/meta original antes dos 15%
crescimento_base = resumo[["LOJA", "BASE_BIMESTRE", "REAL_BIMESTRE"]].copy()
crescimento_base["DIFERENÇA_VS_BASE"] = crescimento_base["REAL_BIMESTRE"] - crescimento_base["BASE_BIMESTRE"]
crescimento_base["%_CRESCIMENTO_VS_BASE"] = np.where(
    crescimento_base["BASE_BIMESTRE"] > 0,
    crescimento_base["DIFERENÇA_VS_BASE"] / crescimento_base["BASE_BIMESTRE"] * 100,
    0,
)
crescimento_base["STATUS_BASE"] = np.where(
    crescimento_base["REAL_BIMESTRE"] >= crescimento_base["BASE_BIMESTRE"],
    "✅ Acima da base",
    "❌ Abaixo da base",
)
crescimento_base = crescimento_base.sort_values("%_CRESCIMENTO_VS_BASE", ascending=False).reset_index(drop=True)
crescimento_base["RANKING_CRESCIMENTO"] = crescimento_base.index + 1

geral_crescimento_base = pd.DataFrame([{
    "LOJA": "TOTAL GERAL",
    "BASE_BIMESTRE": crescimento_base["BASE_BIMESTRE"].sum(),
    "REAL_BIMESTRE": crescimento_base["REAL_BIMESTRE"].sum(),
}])
geral_crescimento_base["DIFERENÇA_VS_BASE"] = geral_crescimento_base["REAL_BIMESTRE"] - geral_crescimento_base["BASE_BIMESTRE"]
geral_crescimento_base["%_CRESCIMENTO_VS_BASE"] = np.where(
    geral_crescimento_base["BASE_BIMESTRE"] > 0,
    geral_crescimento_base["DIFERENÇA_VS_BASE"] / geral_crescimento_base["BASE_BIMESTRE"] * 100,
    0,
)
geral_crescimento_base["STATUS_BASE"] = np.where(
    geral_crescimento_base["REAL_BIMESTRE"] >= geral_crescimento_base["BASE_BIMESTRE"],
    "✅ Acima da base",
    "❌ Abaixo da base",
)

# Premiação por loja: somente lojas que bateram a meta +15% entram na zona de premiação.
lojas_elegiveis = resumo[resumo["REAL_BIMESTRE"] >= resumo["META_15"]].copy()
lojas_elegiveis = lojas_elegiveis.sort_values(["%_ATINGIMENTO", "REAL_BIMESTRE"], ascending=False).reset_index(drop=True)
lojas_elegiveis["COLOCAÇÃO"] = lojas_elegiveis.index + 1

premios_df = pd.DataFrame(PREMIOS, columns=["COLOCAÇÃO", "PRÊMIO", "REGRA"])
premios_df = premios_df.merge(
    lojas_elegiveis[["COLOCAÇÃO", "LOJA", "REAL_BIMESTRE", "META_15", "%_ATINGIMENTO"]],
    on="COLOCAÇÃO",
    how="left",
)
premios_df["INDICATIVO"] = np.where(premios_df["LOJA"].notna(), "🏆 Ganhando no momento", "⚠️ Sem loja elegível")

loja_lider = lojas_elegiveis.iloc[0] if not lojas_elegiveis.empty else None
vendedor_tv = None
if loja_lider is not None:
    top_vendedor_loja = rank_vend_loja[rank_vend_loja["LOJA"] == loja_lider["LOJA"]].sort_values("VR.TOTAL", ascending=False).head(1)
    if not top_vendedor_loja.empty:
        vendedor_tv = top_vendedor_loja.iloc[0]

# Lojas mais próximas de entrar na zona de premiação
proximos = resumo[resumo["REAL_BIMESTRE"] < resumo["META_15"]].copy()
proximos = proximos.sort_values(["%_ATINGIMENTO", "REAL_BIMESTRE"], ascending=False).head(5)

# Prêmios fora por ausência de lojas batendo a meta
premios_fora = premios_df[premios_df["LOJA"].isna()][["COLOCAÇÃO", "PRÊMIO"]].copy()
# =========================
# DASHBOARD
# =========================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Realizado Bimestre", brl(geral["REAL_BIMESTRE"].iloc[0]))
col2.metric("Meta +15%", brl(geral["META_15"].iloc[0]))
col3.metric("Falta para Meta", brl(geral["FALTA_META"].iloc[0]))
col4.metric("Dias restantes", f"{dias_restantes} dia(s)")

st.subheader("Resumo Geral")
st.dataframe(
    geral.assign(**{
        "META_MARCO": geral["META_MARCO"].map(brl),
        "META_ABRIL": geral["META_ABRIL"].map(brl),
        "BASE_BIMESTRE": geral["BASE_BIMESTRE"].map(brl),
        "META_15": geral["META_15"].map(brl),
        "REAL_MARCO": geral["REAL_MARCO"].map(brl),
        "REAL_ABRIL": geral["REAL_ABRIL"].map(brl),
        "REAL_BIMESTRE": geral["REAL_BIMESTRE"].map(brl),
        "FALTA_META": geral["FALTA_META"].map(brl),
        "%_ATINGIMENTO": geral["%_ATINGIMENTO"].map(pct),
        "VENDA_DIA_NECESSARIA": geral["VENDA_DIA_NECESSARIA"].map(brl),
    }),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Resumo por Loja")
resumo_fmt = resumo[["RANKING_LOJA", "LOJA", "REAL_MARCO", "REAL_ABRIL", "REAL_BIMESTRE", "META_15", "FALTA_META", "VENDA_DIA_NECESSARIA", "%_ATINGIMENTO", "STATUS"]].copy()
for c in ["REAL_MARCO", "REAL_ABRIL", "REAL_BIMESTRE", "META_15", "FALTA_META", "VENDA_DIA_NECESSARIA"]:
    resumo_fmt[c] = resumo_fmt[c].map(brl)
resumo_fmt["%_ATINGIMENTO"] = resumo_fmt["%_ATINGIMENTO"].map(pct)
st.dataframe(resumo_fmt, use_container_width=True, hide_index=True)

st.subheader("Ranking Geral de Vendedores")
rank_fmt = rank_vend.copy()
rank_fmt["VR.TOTAL"] = rank_fmt["VR.TOTAL"].map(brl)
st.dataframe(rank_fmt[["RANKING", "VENDEDOR", "VR.TOTAL"]], use_container_width=True, hide_index=True)

st.subheader("Ranking de Vendedores por Loja")
loja_select = st.selectbox("Selecione uma loja para detalhar", options=considerar_lojas)
rv_loja = rank_vend_loja[rank_vend_loja["LOJA"] == loja_select].copy()
rv_loja["VR.TOTAL"] = rv_loja["VR.TOTAL"].map(brl)
st.dataframe(rv_loja[["RANKING_LOJA", "LOJA", "VENDEDOR", "VR.TOTAL"]], use_container_width=True, hide_index=True)

st.subheader("Crescimento no Bimestre vs Base Original")
st.caption("Compara o realizado do CSV no bimestre contra a base/meta original de março + abril, antes do acréscimo de 15%.")
geral_cresc_show = geral_crescimento_base.copy()
for c in ["BASE_BIMESTRE", "REAL_BIMESTRE", "DIFERENÇA_VS_BASE"]:
    geral_cresc_show[c] = geral_cresc_show[c].map(brl)
geral_cresc_show["%_CRESCIMENTO_VS_BASE"] = geral_cresc_show["%_CRESCIMENTO_VS_BASE"].map(pct)
st.dataframe(geral_cresc_show, use_container_width=True, hide_index=True)

cresc_show = crescimento_base.copy()
for c in ["BASE_BIMESTRE", "REAL_BIMESTRE", "DIFERENÇA_VS_BASE"]:
    cresc_show[c] = cresc_show[c].map(brl)
cresc_show["%_CRESCIMENTO_VS_BASE"] = cresc_show["%_CRESCIMENTO_VS_BASE"].map(pct)
st.dataframe(cresc_show[["RANKING_CRESCIMENTO", "LOJA", "BASE_BIMESTRE", "REAL_BIMESTRE", "DIFERENÇA_VS_BASE", "%_CRESCIMENTO_VS_BASE", "STATUS_BASE"]], use_container_width=True, hide_index=True)

st.subheader("Indicativo de Premiação por Loja")
st.caption("A premiação é por colocação das lojas que já bateram a meta de crescimento de 15%. A TV contempla a loja 1ª colocada: 01 TV para o gerente e 01 TV para o vendedor que mais vendeu nessa loja.")
if loja_lider is not None:
    vendedor_msg = f" Vendedor líder da loja: {vendedor_tv['VENDEDOR']} ({brl(vendedor_tv['VR.TOTAL'])})." if vendedor_tv is not None else ""
    st.success(f"Loja líder elegível: {loja_lider['LOJA']} com {pct(loja_lider['%_ATINGIMENTO'])} de atingimento.{vendedor_msg}")
else:
    st.warning("Nenhuma loja bateu a meta de 15% até o momento. Portanto, ainda não há loja elegível para premiação.")
premios_show = premios_df.copy()
for c in ["REAL_BIMESTRE", "META_15"]:
    premios_show[c] = premios_show[c].fillna(0).map(brl)
premios_show["%_ATINGIMENTO"] = premios_show["%_ATINGIMENTO"].fillna(0).map(pct)
st.dataframe(premios_show[["COLOCAÇÃO", "PRÊMIO", "REGRA", "LOJA", "REAL_BIMESTRE", "META_15", "%_ATINGIMENTO", "INDICATIVO"]], use_container_width=True, hide_index=True)

st.subheader("Lojas mais próximas de ganhar prêmio")
if proximos.empty:
    st.success("Todas as lojas analisadas já bateram a meta de 15%.")
else:
    prox_show = proximos.copy()
    for c in ["REAL_BIMESTRE", "META_15", "FALTA_META", "VENDA_DIA_NECESSARIA"]:
        prox_show[c] = prox_show[c].map(brl)
    prox_show["%_ATINGIMENTO"] = prox_show["%_ATINGIMENTO"].map(pct)
    st.dataframe(prox_show[["RANKING_LOJA", "LOJA", "REAL_BIMESTRE", "META_15", "FALTA_META", "VENDA_DIA_NECESSARIA", "%_ATINGIMENTO", "STATUS"]], use_container_width=True, hide_index=True)

st.subheader("Prêmios sem ganhador no momento")
if premios_fora.empty:
    st.success("Todos os prêmios possuem loja elegível no momento.")
else:
    st.info("Os prêmios abaixo ainda estão sem ganhador porque não há lojas suficientes batendo a meta de 15%.")
    st.dataframe(premios_fora, use_container_width=True, hide_index=True)

st.subheader("Base Detalhada")
with st.expander("Ver linhas do CSV tratadas"):
    st.dataframe(base, use_container_width=True, hide_index=True)

# Download Excel
excel = make_excel({
    "Resumo Geral": geral,
    "Resumo Lojas": resumo,
    "Crescimento vs Base": crescimento_base,
    "Ranking Vendedores": rank_vend[["RANKING", "VENDEDOR", "VR.TOTAL"]],
    "Ranking Vend Loja": rank_vend_loja[["LOJA", "RANKING_LOJA", "VENDEDOR", "VR.TOTAL"]],
    "Premiacao Lojas": premios_df,
    "Base Tratada": base,
})
st.download_button(
    label="Baixar análise em Excel",
    data=excel,
    file_name="analise_campanha_3m.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

"""Dashboard de monitoramento (Streamlit) - lê os dados do canal ThingSpeak.

Rodar com:  streamlit run dashboard.py
"""
import streamlit as st

from iot_utils import buscar_feeds, carregar_config, feeds_para_dataframe

FUSO = "America/Sao_Paulo"
INTERVALO_ATUALIZACAO = 20  # segundos

cfg = carregar_config()


def _segredo(nome, padrao=None):
    """Procura primeiro no secrets.toml/variáveis de ambiente e depois nos Secrets do Streamlit Cloud."""
    if cfg.get(nome):
        return cfg[nome]
    try:
        return st.secrets.get(nome, padrao)
    except Exception:
        return padrao


CHANNEL_ID = _segredo("THINGSPEAK_CHANNEL_ID", "3544752")
READ_KEY = _segredo("THINGSPEAK_READ_KEY")

st.set_page_config(page_title="Monitoramento Horta Comunitária", page_icon="🌱", layout="wide")
st.title("🌱 Monitoramento Horta Comunitária")
st.caption(f"Dados do canal ThingSpeak {CHANNEL_ID} • atualiza sozinho a cada {INTERVALO_ATUALIZACAO} s")

with st.sidebar:
    st.header("Configurações")
    limite_temp = st.slider("Limite de temperatura (°C)", 15.0, 45.0, 30.0, 0.5)
    n_pontos = st.slider("Quantidade de leituras no gráfico", 20, 500, 100, 10)
    st.caption("O limite do alerta no ESP32 é 30 °C (variável LIMITE_TEMP no sketch).")

if not READ_KEY:
    st.warning(
        "Read API Key não configurada. Se o canal for privado, copie "
        ".streamlit/secrets.toml.example para .streamlit/secrets.toml e preencha a chave."
    )


@st.fragment(run_every=INTERVALO_ATUALIZACAO)
def painel():
    try:
        payload = buscar_feeds(CHANNEL_ID, READ_KEY, results=n_pontos)
    except Exception as erro:
        st.error(
            "Não consegui ler o canal. Verifique o ID do canal, a Read API Key e a conexão. "
            f"Detalhe: {erro}"
        )
        return

    df = feeds_para_dataframe(payload, FUSO)
    if df.empty:
        st.info("O canal ainda não tem dados. Rode a simulação no Wokwi e aguarde alguns segundos.")
        return

    ultimo = df.iloc[-1]
    temp, umid = ultimo["temperatura"], ultimo["umidade"]

    # Status / alerta visual
    if temp > limite_temp:
        st.error(f"🚨 ALERTA: temperatura de {temp:.1f} °C acima do limite de {limite_temp:.1f} °C")
    else:
        st.success(f"✅ Tudo normal: temperatura de {temp:.1f} °C (limite {limite_temp:.1f} °C)")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperatura atual", f"{temp:.1f} °C")
    c2.metric("Umidade atual", f"{umid:.1f} %")
    c3.metric("Temp. máxima (período)", f"{df['temperatura'].max():.1f} °C")
    c4.metric("Temp. média (período)", f"{df['temperatura'].mean():.1f} °C")
    st.caption(f"Última leitura: {ultimo['momento'].strftime('%d/%m/%Y %H:%M:%S')} • {len(df)} leituras exibidas")

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Temperatura (°C)")
        graf = df.set_index("momento")[["temperatura"]].copy()
        graf["limite"] = limite_temp
        st.line_chart(graf)
    with g2:
        st.subheader("Umidade (%)")
        st.line_chart(df.set_index("momento")[["umidade"]])

    with st.expander("Ver tabela de dados"):
        st.dataframe(df.sort_values("momento", ascending=False), use_container_width=True)
        st.download_button(
            "Baixar dados em CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="leituras.csv",
            mime="text/csv",
        )


painel()

"""Funções compartilhadas pelo dashboard e pelo script de alerta."""
import os
from pathlib import Path

import pandas as pd
import requests

THINGSPEAK_URL = "https://api.thingspeak.com"
CHAVES_CONFIG = [
    "THINGSPEAK_CHANNEL_ID",
    "THINGSPEAK_READ_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
]


def carregar_config():
    """Lê as configurações do arquivo .streamlit/secrets.toml e das variáveis de ambiente.

    As variáveis de ambiente têm prioridade sobre o arquivo.
    """
    cfg = {}
    caminho = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if caminho.exists():
        try:
            try:
                import tomllib  # Python 3.11+
            except ImportError:
                import tomli as tomllib  # Python 3.10 ou anterior
            cfg.update(tomllib.loads(caminho.read_text(encoding="utf-8")))
        except Exception as erro:
            print(f"Aviso: não consegui ler {caminho}: {erro}")
    for chave in CHAVES_CONFIG:
        if os.environ.get(chave):
            cfg[chave] = os.environ[chave]
    return cfg


def buscar_feeds(channel_id, read_key=None, results=100, timeout=10):
    """Busca os últimos registros do canal no ThingSpeak e devolve o JSON."""
    params = {"results": results}
    if read_key:
        params["api_key"] = read_key
    resp = requests.get(
        f"{THINGSPEAK_URL}/channels/{channel_id}/feeds.json",
        params=params,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def feeds_para_dataframe(payload, fuso="America/Sao_Paulo"):
    """Converte o JSON do ThingSpeak em uma tabela com colunas: momento, temperatura, umidade."""
    feeds = payload.get("feeds", []) if isinstance(payload, dict) else []
    colunas = ["momento", "temperatura", "umidade"]
    if not feeds:
        return pd.DataFrame(columns=colunas)

    df = pd.DataFrame(feeds)
    vazio = pd.Series([None] * len(df), index=df.index, dtype="object")
    df["momento"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_convert(fuso)
    df["temperatura"] = pd.to_numeric(df.get("field1", vazio), errors="coerce")
    df["umidade"] = pd.to_numeric(df.get("field2", vazio), errors="coerce")
    df = df[colunas].dropna(subset=["temperatura", "umidade"], how="all")
    return df.sort_values("momento").reset_index(drop=True)


def enviar_telegram(token, chat_id, texto):
    """Envia uma mensagem pelo bot do Telegram. Devolve True se deu certo."""
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": texto},
        timeout=10,
    )
    return resp.ok

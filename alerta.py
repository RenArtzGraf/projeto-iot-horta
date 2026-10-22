"""Monitor de alerta: checa o canal ThingSpeak e avisa quando a temperatura passa do limite.

Se o Telegram estiver configurado, manda a mensagem no celular. Se não, só escreve no terminal.

Rodar com:  python alerta.py
Para parar: Ctrl + C
"""
import time

from iot_utils import buscar_feeds, carregar_config, enviar_telegram, feeds_para_dataframe

LIMITE_TEMP = 30.0       # °C - mesmo valor do sketch do ESP32
INTERVALO_CHECAGEM = 30  # segundos entre cada consulta ao ThingSpeak
PAUSA_ENTRE_AVISOS = 600 # segundos (10 min) para não mandar mensagem repetida


def main():
    cfg = carregar_config()
    channel_id = cfg.get("THINGSPEAK_CHANNEL_ID", "3544752")
    read_key = cfg.get("THINGSPEAK_READ_KEY")
    tg_token = cfg.get("TELEGRAM_BOT_TOKEN")
    tg_chat = cfg.get("TELEGRAM_CHAT_ID")
    usa_telegram = bool(tg_token and tg_chat)

    print(f"Monitorando o canal {channel_id} (limite {LIMITE_TEMP} °C).")
    print("Aviso por Telegram:", "ATIVADO" if usa_telegram else "desativado (só terminal)")

    ultimo_aviso = 0.0
    while True:
        try:
            df = feeds_para_dataframe(buscar_feeds(channel_id, read_key, results=1))
            if df.empty:
                print("Canal sem dados ainda.")
            else:
                leitura = df.iloc[-1]
                temp, umid = leitura["temperatura"], leitura["umidade"]
                hora = leitura["momento"].strftime("%H:%M:%S")
                print(f"[{hora}] temperatura {temp:.1f} °C | umidade {umid:.1f} %")

                if temp > LIMITE_TEMP and time.time() - ultimo_aviso > PAUSA_ENTRE_AVISOS:
                    texto = (
                        f"🚨 ALERTA Horta Comunitária: temperatura em {temp:.1f} °C "
                        f"(limite {LIMITE_TEMP:.1f} °C) às {hora}. Umidade: {umid:.1f} %."
                    )
                    print(texto)
                    if usa_telegram:
                        ok = enviar_telegram(tg_token, tg_chat, texto)
                        print("Telegram enviado." if ok else "Falha ao enviar no Telegram.")
                    ultimo_aviso = time.time()
        except Exception as erro:
            print(f"Erro ao consultar: {erro}")
        time.sleep(INTERVALO_CHECAGEM)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitor encerrado.")

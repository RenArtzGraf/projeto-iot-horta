# Projeto Extensionista - Monitoramento Horta Comunitária (IoT + Cloud + Python)

Fluxo: **ESP32 + DHT22 (Wokwi) → ThingSpeak (nuvem) → Python (dashboard + alerta)**

## Arquivos
- `iot_utils.py`: funções que leem o ThingSpeak e enviam mensagem no Telegram
- `dashboard.py`: painel Streamlit com gráficos, métricas e alerta visual
- `alerta.py`: monitor que avisa por Telegram (ou no terminal) quando a temperatura passa do limite
- `requirements.txt`: bibliotecas necessárias
- `.streamlit/secrets.toml.example`: modelo do arquivo de configuração

## Como rodar no seu computador
1. Instale o Python 3.9 ou mais novo (python.org). Marque "Add Python to PATH" na instalação.
2. Abra o terminal na pasta do projeto e instale as bibliotecas:
   ```
   pip install -r requirements.txt
   ```
3. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e cole sua **Read API Key**.
4. Deixe a simulação do Wokwi rodando (ela envia os dados para o ThingSpeak).
5. Abra o dashboard:
   ```
   streamlit run dashboard.py
   ```
   O navegador abre sozinho em http://localhost:8501.
6. (Opcional) Em outro terminal, rode o monitor de alerta:
   ```
   python alerta.py
   ```

## Alerta no Telegram (opcional)
1. No Telegram, converse com **@BotFather**, envie `/newbot` e siga os passos. Ele devolve o **token** do bot.
2. Mande qualquer mensagem para o seu bot novo.
3. Abra no navegador `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates` e procure o número em `"chat":{"id":...}`. Esse é o **chat id**.
4. Preencha `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no `secrets.toml` e rode `python alerta.py`.

Para testar, suba a temperatura do sensor no Wokwi acima de 30 °C.

## Segurança
- Não coloque `secrets.toml` no GitHub (adicione `.streamlit/secrets.toml` ao `.gitignore`).
- Não mostre a Write API Key nem a Read API Key em prints do relatório.

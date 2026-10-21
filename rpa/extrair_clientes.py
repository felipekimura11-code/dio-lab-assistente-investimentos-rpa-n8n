"""
RPA - Extrai clientes da página web e envia ao Webhook do N8N.
Uso:  python extrair_clientes.py
"""
import requests
from bs4 import BeautifulSoup

URL_CLIENTES = "https://digitalinnovationone.github.io/dio-lab-assistente-investimentos-rpa-n8n/"

# Teste:     http://localhost:5678/webhook-test/assistente-investimentos  (clicar "Listen for test event" antes)
# Produção:  http://localhost:5678/webhook/assistente-investimentos       (workflow ativado)
WEBHOOK_URL = "http://localhost:5678/webhook-test/assistente-investimentos"


def extrair_clientes():
    resposta = requests.get(URL_CLIENTES, timeout=30)
    resposta.raise_for_status()
    soup = BeautifulSoup(resposta.text, "html.parser")

    clientes = []
    for linha in soup.find("table").find_all("tr"):
        colunas = [td.get_text(strip=True) for td in linha.find_all("td")]
        if len(colunas) == 4:
            nome, email, saldo, perfil = colunas
            clientes.append({"nome": nome, "email": email, "saldo": saldo, "perfil": perfil})
    return clientes


def enviar_para_n8n(clientes):
    resposta = requests.post(WEBHOOK_URL, json={"clientes": clientes}, timeout=60)
    resposta.raise_for_status()
    return resposta.json()


if __name__ == "__main__":
    clientes = extrair_clientes()
    print(f"{len(clientes)} clientes extraídos da página.\n")

    resultado = enviar_para_n8n(clientes)
    if isinstance(resultado, dict):
        resultado = resultado.get("data", [resultado]) if "data" in resultado else [resultado]
    if not resultado or not isinstance(resultado[0], dict) or "mensagem" not in resultado[0]:
        import json
        print("Resposta bruta do N8N:", json.dumps(resultado, ensure_ascii=False)[:2000])

    print("Mensagens geradas pelo N8N:\n")
    for item in resultado:
        print(f"[{item.get('perfil')}] {item.get('email')}")
        print(f"  {item.get('mensagem')}\n")

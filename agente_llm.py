import os
import time
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def descobrir_dominios_b2b(nome_produto: str, pais_alvo: str) -> list:
    """Usa o Gemini conectado ao Google Search para achar compradores REAIS."""
    prompt = f"""
    Pesquise na internet as 3 maiores redes de supermercados, atacadistas ou importadoras de alimentos do país: {pais_alvo}.
    Eles devem ser compradores lógicos para o produto: {nome_produto}.
    Retorne APENAS um array JSON contendo os domínios base oficiais dessas empresas (ex: ["carrefour.fr", "walmart.com"]).
    Não invente domínios e não inclua diretórios ou lojas irrelevantes.
    """
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                "temperature": 0.1, 
                "response_mime_type": "application/json",
                "tools": [{"google_search": {}}] # <--- ISSO CONECTA A IA AO GOOGLE
            } 
        )
        return json.loads(response.text)
    except Exception as erro:
        print(f"Erro na busca Google/Gemini: {erro}")
        return []

def gerar_prospeccao_vendas(ncm: str, nome_produto: str, pais_alvo: str, idioma_alvo: str, contexto_db: dict, contatos_hunter: dict) -> str:
    prompt = f"""
    Você é um analista de Comércio Exterior. 
    PRODUTO: {nome_produto} (NCM: {ncm}) | MERCADO ALVO: {pais_alvo}
    
    DADOS TARIFÁRIOS: {contexto_db}
    CONTATOS ENCONTRADOS: {contatos_hunter}

    ENTREGÁVEIS:
    1. Estratégia B2B: Defenda {pais_alvo} usando os dados tarifários reais. Sem invenções.
    2. Carta (Cold Email) em {idioma_alvo}: Direcione a carta aos contatos encontrados.
    """
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={"temperature": 0.1} 
            )
            return response.text
        except Exception as erro:
            if "503" in str(erro) and tentativa < tentativas - 1:
                time.sleep(3)
                continue
            raise erro
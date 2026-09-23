import os
import time
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def descobrir_dominios_b2b(nome_produto: str, pais_alvo: str) -> list:
    """Usa o Gemini conectado ao Google Search para encontrar compradores corporativos REAIS."""
    prompt = f"""
    Pesquise no Google as 3 maiores redes de supermercados, atacadistas ou grandes empresas importadoras com foco em distribuição B2B no país: {pais_alvo}.
    Eles devem ser compradores lógicos e reais para o produto: {nome_produto}.
    IMPORTANTE: Exclua retalhistas pequenos, restaurantes locais, cafés, peixarias ou menus online. Queremos apenas grandes importadores corporativos.
    Retorne APENAS um array JSON válido contendo os domínios base oficiais destas empresas (exemplo: ["nkg.coffee", "rewe.de"]).
    Não invente domínios e não inclua qualquer texto extra além do JSON.
    """
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                "temperature": 0.1, 
                "response_mime_type": "application/json",
                "tools": [{"google_search": {}}] # Ativa o Google Search Grounding nativo do Gemini
            } 
        )
        return json.loads(response.text)
    except Exception as erro:
        print(f"Erro na busca Google/Gemini: {erro}")
        return []

def gerar_prospeccao_vendas(ncm: str, nome_produto: str, pais_alvo: str, idioma_alvo: str, contexto_db: dict, contatos_hunter: dict) -> str:
    """Gera a estratégia e o e-mail cruzando os dados do Parquet com os e-mails do Hunter."""
    prompt = f"""
    Você é um analista de Comércio Exterior de alto nível. 
    
    PRODUTO: {nome_produto} (NCM: {ncm}) | MERCADO ALVO: {pais_alvo}
    DADOS TARIFÁRIOS: {contexto_db}
    CONTATOS REAIS ENCONTRADOS: {contatos_hunter}

    ENTREGÁVEIS OBRIGATÓRIOS:
    1. Estratégia B2B: Justifique {pais_alvo} usando estritamente os dados tarifários reais fornecidos. Sem invenções.
    2. Carta (Cold Email) em {idioma_alvo}: Direcione a carta aos contatos encontrados. Utilize um tom profissional de negócios.
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
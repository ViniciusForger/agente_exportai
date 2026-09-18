import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def gerar_prospeccao_vendas(ncm: str, nome_produto: str, pais_alvo: str, idioma_alvo: str, contexto_db: dict, contatos_hunter: list) -> str:
    prompt = f"""
    Você é um especialista em Comércio Exterior B2B.
    
    DADOS DO PRODUTO:
    - Produto: {nome_produto} (NCM: {ncm})
    - Mercado Alvo: {pais_alvo}
    
    DADOS DE EXPORTAÇÃO (Extraídos do Banco de Dados Interno):
    - {contexto_db}
    
    CONTATOS DE PROSPECÇÃO (Extraídos do Hunter.io):
    - {contatos_hunter}

    Sua tarefa:
    1. Estratégia B2B: Explique por que focar em {pais_alvo} é ideal para este produto e recomende 3 tipos de parceiros locais.
    2. Carta de Apresentação (Cold Email): Escreva um e-mail persuasivo no idioma {idioma_alvo}. 
    ATENÇÃO: Integre as informações de exportação (alíquotas/exigências) na carta para demonstrar autoridade. Direcione o e-mail para um dos contatos reais fornecidos na lista acima, se disponíveis.
    """
    
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )
            return response.text
        except Exception as erro:
            if "503" in str(erro) and tentativa < tentativas - 1:
                time.sleep(3)
                continue
            raise erro
import os
import time
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def descobrir_dominios_b2b(nome_produto: str, pais_alvo: str) -> list:
    """Usa o Gemini conectado ao Google Search com foco estrito em Importadores B2B."""
    prompt = f"""
    Execute uma pesquisa real no Google para encontrar 3 empresas que sejam estritamente IMPORTADORAS B2B, DISTRIBUIDORAS CORPORATIVAS ou ATACADISTAS do produto '{nome_produto}' no mercado: {pais_alvo}.
    
    REGRAS ABSOLUTAS (SOB PENA DE FALHA):
    1. ZERO VAREJO/RETALHO: É estritamente proibido listar redes de supermercados (ex: Aldi, Rewe, Lidl, Carrefour, Walmart). Procure os importadores B2B que abastecem o retalho.
    2. ZERO ALUCINAÇÃO: Só inclua um domínio se ele for de uma empresa real que você acabou de validar na sua pesquisa do Google.
    3. PRECISÃO: Exclua associações, governos, peixarias ou restaurantes. Queremos apenas empresas de comércio exterior/distribuição.
    
    Retorne APENAS um array JSON válido contendo os domínios base (sem https, sem www). 
    Exemplo de formato: ["importador-real.de", "distribuidora-b2b.com", "grupo-atacadista.fr"]
    Não inclua nenhum texto adicional além do JSON.
    """
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                "temperature": 0.0, 
                "response_mime_type": "application/json",
                "tools": [{"google_search": {}}] 
            } 
        )
        return json.loads(response.text)
    except Exception as erro:
        print(f"Erro na busca Google/Gemini: {erro}")
        return []

def gerar_prospeccao_vendas(ncm: str, nome_produto: str, pais_alvo: str, idioma_alvo: str, contexto_db: dict, dominios_reais: list, contatos_hunter: dict) -> str:
    """Gera a estratégia e o e-mail blindando contra listas inventadas."""
    prompt = f"""
    Você é um analista de Comércio Exterior. 
    
    PRODUTO: {nome_produto} (NCM: {ncm}) | MERCADO ALVO: {pais_alvo}
    DADOS TARIFÁRIOS REAIS: {contexto_db}
    DOMÍNIOS ALVO PESQUISADOS: {dominios_reais}
    E-MAILS ENCONTRADOS: {contatos_hunter}

    ENTREGÁVEIS OBRIGATÓRIOS:
    1. Estratégia B2B Data-Driven: Justifique {pais_alvo} usando ESTRITAMENTE os dados tarifários reais.
    [REGRA ABSOLUTA]: É PROIBIDO criar tópicos listando "Empresas Potenciais", "Organizações", "Associações" ou qualquer nome de empresa. Foque apenas na análise de mercado e impostos. Não invente nomes.

    2. Carta de Apresentação (Cold Email) em {idioma_alvo}:
       - Direcione a carta aos e-mails encontrados.
       - Utilize os dados de impostos como argumento de venda.
    """
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={"temperature": 0.0} # Temperatura ZERO no redator também
            )
            return response.text
        except Exception as erro:
            if "503" in str(erro) and tentativa < tentativas - 1:
                time.sleep(3)
                continue
            raise erro
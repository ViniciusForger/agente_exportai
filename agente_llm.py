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

def gerar_prospeccao_vendas(ncm: str, nome_produto: str, pais_alvo: str, idioma_alvo: str, contexto_db: dict, dominios_reais: list, contatos_hunter: dict, quantidade: str, perfil_parceiro: str) -> str:
    prompt = f"""
    Você é um analista de Comércio Exterior de alto nível. 
    
    PRODUTO: {nome_produto} (NCM: {ncm}) 
    VOLUME DISPONÍVEL: {quantidade}
    MERCADO ALVO: {pais_alvo}
    PERFIL DE PARCEIRO BUSCADO: {perfil_parceiro}
    DADOS TARIFÁRIOS REAIS: {contexto_db}
    
    DOMÍNIOS REAIS JÁ ENCONTRADOS PELO SISTEMA: {dominios_reais}
    E-MAILS CAPTURADOS: {contatos_hunter}

    [REGRA ABSOLUTA - RISCO DE FALHA CRÍTICA]: 
    É ESTRITAMENTE PROIBIDO gerar tópicos listando "Empresas a Validar", "Organizações", "Associações", "Cámaras" ou qualquer nome de empresa. O sistema backend já fez a busca real. Sua única função é escrever o texto abaixo.

    ENTREGÁVEIS OBRIGATÓRIOS:
    1. Estratégia de Mercado: Justifique a viabilidade de exportar {quantidade} para {pais_alvo} focando no perfil {perfil_parceiro}, baseando-se EXCLUSIVAMENTE nos dados tarifários.
    2. Carta de Apresentação (Cold Email) em {idioma_alvo}: Direcione a carta de forma profissional aos e-mails capturados.
    """
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={"temperature": 0.0} 
            )
            return response.text
        except Exception as erro:
            if "503" in str(erro) and tentativa < tentativas - 1:
                time.sleep(3)
                continue
            raise erro
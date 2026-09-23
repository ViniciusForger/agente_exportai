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
    4. ZERO EQUIPAMENTOS/MÁQUINAS: Exclua sumariamente empresas de venda, reparação ou peças para máquinas de café, moinhos, torrefadoras industriais ou equipamento gastronómico. O alvo é ESTRITAMENTE quem compra a MATÉRIA-PRIMA/ALIMENTO.
    
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
    """Gera o Plano Estratégico completo, mas restringe as empresas aos dados reais capturados."""
    prompt = f"""
    Você é um consultor Sênior de Comércio Exterior desenvolvendo um Plano Comercial B2B.
    
    PARÂMETROS DA EXPORTAÇÃO:
    PRODUTO: {nome_produto} (NCM: {ncm}) 
    VOLUME DISPONÍVEL: {quantidade}
    MERCADO ALVO: {pais_alvo}
    PERFIL DO PARCEIRO: {perfil_parceiro}
    DADOS TARIFÁRIOS (Reais): {contexto_db}
    
    DADOS DE PROSPECÇÃO (Validados pelo Sistema):
    EMPRESAS REAIS ENCONTRADAS: {dominios_reais}
    E-MAILS CAPTURADOS: {contatos_hunter}

    Sua tarefa é gerar um Plano Estratégico estruturado. 
    
    [REGRA ABSOLUTA DE DADOS - RISCO DE FALHA]: 
    No tópico 2, você SÓ PODE listar as empresas que estão na variável EMPRESAS REAIS ENCONTRADAS. É estritamente proibido inventar nomes, adicionar associações governamentais, câmaras de comércio ou citar outras marcas que não estejam nessa lista.

    Gere o relatório EXATAMENTE com a seguinte estrutura:

    1. Principais Canais de Distribuição
    Analise os melhores canais para escoar {quantidade} de {nome_produto} na {pais_alvo}, considerando o perfil {perfil_parceiro}.

    2. Empresas Potenciais a Validar
    Liste APENAS as empresas fornecidas na variável EMPRESAS REAIS ENCONTRADAS. Crie uma breve justificativa factual de por que elas se encaixam como boas compradoras para este produto. Inclua os domínios.

    3. Notícias, Tendências e Mudanças Regulatórias
    Analise o consumo local e utilize os DADOS TARIFÁRIOS fornecidos para explicar regras de importação e impostos.

    4. Oportunidades e Riscos
    Liste prós e contras reais da exportação deste produto para este mercado.

    5. Plano de Ação em 30 Dias
    Um checklist tático (semanal) para fechar negócio.

    6. E-mail Inicial de Prospecção
    Escreva um Cold Email B2B altamente persuasivo em {idioma_alvo}, focado em vender para os diretores dos E-MAILS CAPTURADOS.
    """
    
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={"temperature": 0.1} # Temperatura baixa para garantir a obediência às regras
            )
            return response.text
        except Exception as erro:
            if "503" in str(erro) and tentativa < tentativas - 1:
                time.sleep(3)
                continue
            raise erro
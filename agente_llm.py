import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def gerar_prospeccao_vendas(ncm: str, nome_produto: str, pais_alvo: str, idioma_alvo: str) -> str:
    prompt = f"""
    Você é um especialista em Comércio Exterior e Vendas B2B internacionais.
    O usuário deseja exportar o produto '{nome_produto}' (Código NCM: {ncm}) para o mercado alvo: {pais_alvo}.

    Sua tarefa é focar no módulo de Vendas Estratégicas e entregar as quatro etapas abaixo:

    1. Justificativa do Mercado Alvo:
    - Explique estrategicamente por que focar em {pais_alvo} é uma excelente escolha no momento atual para este produto (NCM).

    2. Análise de País Alternativo (Prós e Contras):
    - Sugira um segundo país (diferente de {pais_alvo}) que também tenha alto potencial de importação para este produto.
    - Apresente os prós e contras de investir nesse país alternativo em vez de focar no mercado principal.

    3. Prospecção Ativa B2B em {pais_alvo}:
    - Identifique e liste os 3 melhores tipos de parceiros comerciais locais em {pais_alvo} para este produto.
    - Explique brevemente por que cada perfil é o comprador ideal.

    4. Carta de Apresentação Comercial (Cold Email):
    - Escreva um e-mail persuasivo e profissional de primeiro contato.
    - O e-mail DEVE ser escrito inteiramente no idioma: {idioma_alvo}.
    - Destaque o produto, proponha uma parceria e inclua espaços para personalização.
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
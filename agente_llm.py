import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def gerar_prospeccao_vendas(ncm: str, nome_produto: str, pais_alvo: str, idioma_alvo: str) -> str:
    prompt = f"""
    Você é um especialista em Comércio Exterior e Vendas B2B internacionais.
    O usuário deseja exportar o produto '{nome_produto}' (Código NCM: {ncm}) para o seguinte mercado: {pais_alvo}.

    Sua tarefa é focar exclusivamente no módulo de Vendas e entregar as duas etapas abaixo:

    1. Prospecção Ativa B2B:
    - Identifique e liste os 3 melhores tipos de parceiros comerciais locais em {pais_alvo} (ex: distribuidores, atacadistas, redes de varejo, indústrias) para este produto.
    - Explique brevemente por que cada perfil é o comprador ideal para este NCM.

    2. Carta de Apresentação Comercial (Cold Email):
    - Escreva um e-mail persuasivo e profissional de primeiro contato, direcionado a um desses parceiros ideais.
    - O e-mail DEVE ser escrito inteiramente no idioma: {idioma_alvo}.
    - O e-mail deve destacar o produto, propor uma parceria e incluir espaços para personalização (ex: [Nome da Empresa Alvo]).
    
    Retorne o resultado de forma clara e bem estruturada.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    return response.text
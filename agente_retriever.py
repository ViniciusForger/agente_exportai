import os
import requests
import duckdb
from urllib.parse import urlparse
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

def buscar_dados_internos(ncm: str):
    """Lê as tarifas reais diretamente do seu repositório no Hugging Face."""
    try:
        con = duckdb.connect(database=':memory:')
        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")
        url_parquet = "https://huggingface.co/datasets/ViniForger/importacoes-tarifas-brasil/resolve/main/fato_importacoes_tarifas.parquet"
        query = f"SELECT * FROM read_parquet('{url_parquet}') WHERE ncm = '{ncm}' LIMIT 1"
        resultado = con.execute(query).df()
        con.close()
        
        if not resultado.empty:
            return resultado.iloc[0].to_dict()
        return {"aviso": "Nenhum dado tarifário encontrado para este NCM."}
    except Exception as erro:
        return {"erro_leitura_db": str(erro)}

def buscar_sites_reais(nome_produto: str, pais_alvo: str) -> list:
    """Faz uma busca na internet pelos maiores importadores do produto."""
    termo = f"distributor OR importer {nome_produto} {pais_alvo}"
    dominios = []
    try:
        resultados = DDGS().text(termo, max_results=3)
        for r in resultados:
            url = r.get('href', '')
            if url:
                # Extrai apenas o domínio principal (ex: www.empresa.com -> empresa.com)
                dominio = urlparse(url).netloc.replace('www.', '')
                if dominio not in dominios:
                    dominios.append(dominio)
        return dominios
    except Exception:
        return []

def buscar_leads_hunter(dominio_empresa: str):
    """Busca e-mails do domínio no Hunter.io."""
    url = f"https://api.hunter.io/v2/domain-search?domain={dominio_empresa}&api_key={HUNTER_API_KEY}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        emails = [email['value'] for email in dados.get('data', {}).get('emails', [])[:3]]
        return emails if emails else []
    return []
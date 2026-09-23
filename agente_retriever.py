import os
import requests
import duckdb
from dotenv import load_dotenv

load_dotenv()
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

def buscar_dados_internos(ncm: str):
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

def buscar_leads_hunter(dominio_empresa: str):
    url = f"https://api.hunter.io/v2/domain-search?domain={dominio_empresa}&api_key={HUNTER_API_KEY}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        emails = [email['value'] for email in dados.get('data', {}).get('emails', [])[:3]]
        return emails if emails else []
    return []
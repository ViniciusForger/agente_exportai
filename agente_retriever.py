import os
import requests
import duckdb
from dotenv import load_dotenv

load_dotenv()
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

def buscar_dados_internos(ncm: str):
    """Consulta dados de tarifas de importação diretamente no Hugging Face (Online)."""
    try:
        con = duckdb.connect(database=':memory:')
        
        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")
        
        url_parquet = "https://huggingface.co/datasets/ViniForger/importacoes-tarifas-brasil/resolve/main/fato_importacoes_tarifas.parquet"
        
        query = f"""
            SELECT * 
            FROM read_parquet('{url_parquet}')
            WHERE ncm = '{ncm}' -- Substitua pelo nome exato da coluna no seu arquivo se necessário
            LIMIT 1
        """
        
        resultado = con.execute(query).df()
        con.close()
        
        if not resultado.empty:
            dados_reais = resultado.iloc[0].to_dict()
            return dados_reais
            
        return {"aviso": "Nenhum dado tarifário encontrado para este NCM no repositório."}
        
    except Exception as erro:
        return {"erro_leitura_db": f"Falha ao acessar o arquivo online: {str(erro)}"}


def buscar_leads_hunter(dominio_empresa: str):
    """Busca e-mails reais de tomadores de decisão via Hunter.io."""
    if not dominio_empresa:
        return "Nenhum domínio fornecido para busca de contatos."
        
    url = f"https://api.hunter.io/v2/domain-search?domain={dominio_empresa}&api_key={HUNTER_API_KEY}"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        emails = [email['value'] for email in dados['data']['emails'][:3]]
        return emails if emails else "Nenhum e-mail encontrado neste domínio."
    return "Falha na comunicação com a API de contatos B2B."
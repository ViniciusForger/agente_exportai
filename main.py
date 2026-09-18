from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agente_llm import gerar_prospeccao_vendas
from agente_retriever import buscar_dados_internos, buscar_leads_hunter

app = FastAPI(title="ExportAI - Módulo Vendas B2B")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VendasRequest(BaseModel):
    ncm: str
    nome_produto: str
    pais_alvo: str
    idioma_alvo: str
    dominio_alvo: Optional[str] = None  # Ex: "aldi.de"

@app.post("/vendas/prospeccao")
async def prospeccao_vendas(request: VendasRequest):
    try:
        # 1. Busca dados internos (DuckDB)
        dados_tecnicos = buscar_dados_internos(request.ncm)
        
        # 2. Busca contatos reais (Hunter.io)
        contatos = buscar_leads_hunter(request.dominio_alvo)
        
        # 3. Gera análise e e-mail com Gemini (RAG)
        resultado = gerar_prospeccao_vendas(
            request.ncm, 
            request.nome_produto, 
            request.pais_alvo, 
            request.idioma_alvo,
            dados_tecnicos,
            contatos
        )
        
        return {
            "status": "sucesso", 
            "leads_encontrados": contatos,
            "relatorio": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
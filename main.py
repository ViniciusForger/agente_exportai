from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agente_llm import gerar_prospeccao_vendas

app = FastAPI(title="ExportAI - Módulo Vendas")

# Configuração para permitir que o Lovable acesse a API
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

@app.post("/vendas/prospeccao")
async def prospeccao_vendas(request: VendasRequest):
    try:
        resultado = gerar_prospeccao_vendas(
            request.ncm, 
            request.nome_produto, 
            request.pais_alvo, 
            request.idioma_alvo
        )
        return {"status": "sucesso", "relatorio": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
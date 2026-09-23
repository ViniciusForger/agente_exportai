from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agente_llm import descobrir_dominios_b2b, gerar_prospeccao_vendas
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

@app.post("/vendas/prospeccao")
async def prospeccao_vendas(request: VendasRequest):
    try:
        dados_tecnicos = buscar_dados_internos(request.ncm)
        
        # 1. IA faz pesquisa semântica no Google (Fugindo das peixarias)
        dominios_descobertos = descobrir_dominios_b2b(request.nome_produto, request.pais_alvo)
        
        # 2. Hunter varre os sites reais
        contatos_finais = {}
        for dominio in dominios_descobertos:
            emails = buscar_leads_hunter(dominio)
            if emails:
                contatos_finais[dominio] = emails
                
        # 3. IA escreve a carta com tudo integrado
        resultado = gerar_prospeccao_vendas(
            request.ncm, 
            request.nome_produto, 
            request.pais_alvo, 
            request.idioma_alvo,
            dados_tecnicos,
            contatos_finais
        )
        
        return {
            "status": "sucesso",
            "empresas_alvo": dominios_descobertos,
            "leads_encontrados": contatos_finais,
            "relatorio": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
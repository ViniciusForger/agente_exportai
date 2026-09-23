from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agente_llm import gerar_prospeccao_vendas
from agente_retriever import buscar_dados_internos, buscar_sites_reais, buscar_leads_hunter

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
        
        # 1. Pesquisa os sites ao vivo
        dominios_encontrados = buscar_sites_reais(request.nome_produto, request.pais_alvo)
        
        # 2. Extrai os e-mails via Hunter para cada site
        contatos_finais = {}
        for dominio in dominios_encontrados:
            emails = buscar_leads_hunter(dominio)
            if emails:
                contatos_finais[dominio] = emails
                
        # 3. Gera a carta baseada em fatos
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
            "empresas_reais_pesquisadas": dominios_encontrados,
            "leads_encontrados": contatos_finais,
            "relatorio": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
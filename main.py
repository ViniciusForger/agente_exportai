from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agente_llm import AgenteImportacaoLLM

app = FastAPI(title="ExportAI API", version="1.0")

# Libera o CORS para permitir que o frontend do Lovable acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o agente de IA
try:
    agente = AgenteImportacaoLLM()
except Exception as e:
    print(f"Erro ao carregar o agente: {e}")

class ConsultaRequest(BaseModel):
    ncm: str
    pergunta: str
    top_n: int = 3

@app.get("/")
def home():
    return {"status": "online", "message": "API do ExportAI rodando com sucesso!"}

@app.post("/analisar")
def analisar_importacao(dados: ConsultaRequest):
    try:
        resposta = agente.gerar_conselho(
            pergunta=dados.pergunta, 
            ncm=dados.ncm.strip(), 
            top_n=dados.top_n
        )
        return {"status": "sucesso", "relatorio": resposta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
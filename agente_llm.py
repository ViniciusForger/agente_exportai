import os
from google import genai
from dotenv import load_dotenv
from agente_retriever import ImportDataRetriever

load_dotenv()

class AgenteImportacaoLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Chave GEMINI_API_KEY não encontrada no arquivo .env.")
            
        self.client = genai.Client(api_key=api_key)
        self.retriever = ImportDataRetriever()
        self.modelo = "gemini-3.6-flash"

    def gerar_conselho(self, pergunta: str, ncm: str, top_n: int = 5):
        contexto_dados = self.retriever.buscar_melhores_fornecedores(ncm=ncm, top_n=top_n)

        instrucoes_sistema = """Você é o Assistente Especialista de Importação sênior do ExportAI.
Sua missão é fornecer uma consultoria estratégica profunda para empresários brasileiros com base ESTRITAMENTE nos dados fornecidos.
REGRAS RÍGIDAS DE ANÁLISE:
- NUNCA invente países, valores, tarifas ou fornecedores que não estejam no contexto.
- USE EXCLUSIVAMENTE O NOME DO PAÍS fornecido nos dados (Ex: Índia, China, Estados Unidos). É terminantemente proibido utilizar códigos numéricos.
- DETALHE O PASSO A PASSO: Explique detalhadamente por que o país principal foi escolhido (vantagens combinadas de FOB e frete, liquidez de mercado) e por que os demais concorrentes foram deixados em segundo plano (desvantagens de custo ou logística mais cara).
- Estruture a resposta de forma executiva, clara e profissional.
- Conclua abrindo a possibilidade de avançar para a etapa de negociação comercial com o país escolhido ou outro de preferência do empresário."""

        prompt_usuario = f"""
[CONTEXTO DE DADOS GOVERNAMENTAIS - EXPORTAI]
{contexto_dados}

PERGUNTA DO EMPRESÁRIO: {pergunta}
Baseado estritamente nos dados acima, elabore um relatório detalhado justificando a escolha e os trade-offs de cada rota.
"""
        print("🧠 [Agente] Gerando relatório estratégico detalhado com Gemini...")

        resposta = self.client.models.generate_content(
            model=self.modelo,
            contents=prompt_usuario,
            config={
                'system_instruction': instrucoes_sistema,
                'temperature': 0.2,
            }
        )

        return resposta.text

if __name__ == "__main__":
    agente = AgenteImportacaoLLM()
    pergunta = "Estou querendo importar esse produto. Olhando os dados de frete e preço, qual país oferece a melhor opção?"
    
    conselho = agente.gerar_conselho(pergunta=pergunta, ncm="07129010", top_n=3)
    
    print("\n" + "="*50)
    print("💡 RESPOSTA FINAL DA INTELIGÊNCIA ARTIFICIAL:")
    print("="*50)
    print(conselho)
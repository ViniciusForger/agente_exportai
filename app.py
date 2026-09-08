import os
import streamlit as st
from dotenv import load_dotenv
from agente_llm import AgenteImportacaoLLM

load_dotenv()

st.set_page_config(
    page_title="ExportAI - Assistente de Importação",
    page_icon="🚢",
    layout="centered"
)

@st.cache_resource
def carregar_agente():
    return AgenteImportacaoLLM()

try:
    agente = carregar_agente()
except Exception as e:
    st.error(f"Erro ao inicializar o agente: {e}")
    st.stop()

st.title("🚢 ExportAI")
st.markdown("### Seu Assistente Inteligente de Estratégia de Importação")
st.write("Consulte dados oficiais do comércio exterior brasileiro e receba análises estratégicas detalhadas por Inteligência Artificial.")

col1, col2 = st.columns([2, 1])
with col1:
    ncm_input = st.text_input("Código NCM do Produto:", value="07129010", max_chars=8, help="Digite o código NCM de 8 dígitos do produto.")
with col2:
    top_n_input = st.selectbox("Top Fornecedores:", [3, 5, 10], index=0)

pergunta_usuario = st.text_area(
    "O que você gostaria de saber sobre a importação deste produto?",
    value="Quero entender a fundo qual é a melhor rota de importação, comparando detalhadamente as vantagens e desvantagens de cada país fornecedor."
)

if st.button("🚀 Gerar Análise Estratégica Completa", type="primary"):
    if not ncm_input or len(ncm_input) < 8:
        st.warning("Por favor, insira um código NCM válido com 8 dígitos.")
    else:
        with st.spinner("🔍 Consultando base na nuvem e processando relatório estratégico com IA..."):
            try:
                resposta_ia = agente.gerar_conselho(
                    pergunta=pergunta_usuario, 
                    ncm=ncm_input.strip(), 
                    top_n=top_n_input
                )
                
                st.session_state['resultado_ia'] = resposta_ia
                st.session_state['analise_concluida'] = True
                
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a solicitação: {e}")

if st.session_state.get('analise_concluida', False):
    st.markdown("---")
    st.markdown("### 💡 Relatório Estratégico Detalhado ExportAI")
    st.markdown(st.session_state['resultado_ia'])
    
    st.markdown("---")
    st.markdown("### 🤝 Deseja avançar para Negociação Comercial?")
    st.write("Selecione o país com o qual deseja fechar negócio ou iniciar tratativas logísticas:")
    
    pais_escolhido = st.text_input("Digite o nome do país de sua preferência:", value="Índia")
    volume_estimado = st.number_input("Volume estimado de importação (em kg):", min_value=100, value=5000, step=500)
    
    if st.button("📋 Gerar Minuta de Carta de Intenção / Roteiro de Contato"):
        with st.spinner("Gerando direcionamento comercial..."):
            prompt_negocio = f"""
            O empresário brasileiro decidiu avançar nas tratativas comerciais para importar o produto NCM {ncm_input} com o seguinte país: {pais_escolhido}.
            O volume estimado para a importação é de {volume_estimado} kg.
            Gere um roteiro comercial prático contendo:
            1. Próximos passos práticos para contato com fornecedores desse país.
            2. Pontos de atenção sobre documentação alfandegária e frete internacional para este volume.
            3. Um modelo em inglês de mensagem/e-mail formal de consulta comercial (RFQ - Request for Quotation) direcionada a um fornecedor internacional.
            """
            plano_comercial = agente.client.models.generate_content(
                model=agente.modelo,
                contents=prompt_negocio,
                config={'temperature': 0.3}
            )
            st.markdown("#### 📄 Roteiro e Plano de Ação Comercial")
            st.markdown(plano_comercial.text)
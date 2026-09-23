def gerar_prospeccao_vendas(ncm: str, nome_produto: str, pais_alvo: str, idioma_alvo: str, contexto_db: dict, dominios_reais: list, contatos_hunter: dict) -> str:
    """Gera a estratégia e o e-mail blindando contra listas inventadas."""
    prompt = f"""
    Você é um analista de Comércio Exterior. 
    
    PRODUTO: {nome_produto} (NCM: {ncm}) | MERCADO ALVO: {pais_alvo}
    DADOS TARIFÁRIOS REAIS: {contexto_db}
    DOMÍNIOS ALVO PESQUISADOS: {dominios_reais}
    E-MAILS ENCONTRADOS: {contatos_hunter}

    ENTREGÁVEIS OBRIGATÓRIOS:
    1. Estratégia B2B Data-Driven: Justifique {pais_alvo} usando ESTRITAMENTE os dados tarifários reais.
    [REGRA ABSOLUTA]: É PROIBIDO criar tópicos listando "Empresas Potenciais", "Organizações", "Associações" ou qualquer nome de empresa. Foque apenas na análise de mercado e impostos. Não invente nomes.

    2. Carta de Apresentação (Cold Email) em {idioma_alvo}:
       - Direcione a carta aos e-mails encontrados.
       - Utilize os dados de impostos como argumento de venda.
    """
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={"temperature": 0.0} # Temperatura ZERO no redator também
            )
            return response.text
        except Exception as erro:
            if "503" in str(erro) and tentativa < tentativas - 1:
                time.sleep(3)
                continue
            raise erro
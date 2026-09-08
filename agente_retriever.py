import duckdb
import pandas as pd

class ImportDataRetriever:
    def __init__(self):
        self.conn = duckdb.connect(database=':memory:')
        
        self.conn.execute("INSTALL httpfs;")
        self.conn.execute("LOAD httpfs;")
        
        self.arq_importacoes = 'https://huggingface.co/datasets/ViniForger/importacoes-tarifas-brasil/resolve/main/fato_importacoes_tarifas.parquet'
        self.arq_indice = 'https://huggingface.co/datasets/ViniForger/importacoes-tarifas-brasil/resolve/main/indice_ncm_hs6.parquet'
        
        # Dicionário de tradução oficial de códigos do Comex Stat para nomes de países
        self.paises_map = {
            '160': 'China',
            '249': 'Estados Unidos',
            '361': 'Índia',
            '087': 'Bélgica',
            '573': 'Países Baixos (Holanda)',
            '063': 'Argentina',
            '275': 'França',
            '245': 'Espanha',
            '386': 'Itália',
            '399': 'Japão',
            '639': 'Reino Unido',
            '149': 'Canadá',
            '589': 'Peru',
            '858': 'Uruguai',
            '105': 'Brasil',
            '756': 'África do Sul',
            '630': 'Portugal',
            '169': 'Colômbia',
            '493': 'México',
            '791': 'Coreia do Sul'
        }

    def traduzir_pais(self, codigo):
        cod_str = str(codigo).zfill(3)
        return self.paises_map.get(cod_str, f"Parceiro Internacional ({cod_str})")

    def buscar_melhores_fornecedores(self, ncm: str, top_n: int = 5):
        print(f"🔍 [Retriever] Lendo dados do Hugging Face para o NCM: {ncm}...")
        
        query_ncm = f"""
            SELECT HS6, descricao_ncm 
            FROM '{self.arq_indice}' 
            WHERE NCM = '{ncm}'
        """
        ncm_result = self.conn.execute(query_ncm).fetchdf()
        
        if ncm_result.empty:
            return f"❌ Erro: NCM {ncm} não encontrado."
            
        hs6_code = ncm_result['HS6'].iloc[0]
        descricao = ncm_result['descricao_ncm'].iloc[0]

        query_importacoes = f"""
            SELECT 
                imp.CO_PAIS,
                SUM(imp.VL_FOB) as volume_fob_total,
                SUM(imp.VL_FRETE) as custo_frete_total,
                SUM(imp.KG_LIQUIDO) as peso_total,
                MAX(imp.PERCENTUAL_II) as imposto_importacao
            FROM '{self.arq_importacoes}' imp
            WHERE imp.CO_NCM = '{ncm}'
            GROUP BY imp.CO_PAIS
            ORDER BY volume_fob_total DESC
            LIMIT {top_n}
        """
        fornecedores_result = self.conn.execute(query_importacoes).fetchdf()

        if fornecedores_result.empty:
            return f"⚠️ Aviso: Não há histórico de importações para o NCM {ncm}."

        contexto_llm = f"**Produto:** {descricao} (NCM: {ncm} | HS6: {hs6_code})\n"
        tarifa = fornecedores_result['imposto_importacao'].iloc[0]
        contexto_llm += f"**Imposto de Importação (II) na TEC:** {tarifa}%\n\n"
        contexto_llm += f"**TOP {top_n} MAIORES FORNECEDORES PARA O BRASIL:**\n"
        
        for idx, row in fornecedores_result.iterrows():
            fob = row['volume_fob_total']
            peso = row['peso_total']
            preco_kg = fob / peso if peso > 0 else 0
            frete_kg = row['custo_frete_total'] / peso if peso > 0 else 0
            
            nome_pais = self.traduzir_pais(row['CO_PAIS'])

            # Omitimos o código numérico no texto entregue para forçar o uso exclusivo do nome do país
            contexto_llm += (
                f"{idx+1}. País Fornecedor: {nome_pais}\n"
                f"   - Volume FOB Total: US$ {fob:,.2f}\n"
                f"   - Preço Médio FOB: US$ {preco_kg:,.2f}/kg\n"
                f"   - Custo Frete Médio: US$ {frete_kg:,.2f}/kg\n\n"
            )
            
        return contexto_llm
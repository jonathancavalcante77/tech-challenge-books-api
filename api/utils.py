# -*- coding: utf-8 -*-
"""
Funcoes utilitarias para a API.

Foca principalmente na leitura e manipulacao dos dados do CSV.
Separei aqui para nao poluir o arquivo principal da API (main.py).
"""

import os
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any

# Importando constantes do nosso arquivo de configuracao original, assim mantemos consistencia entre o scraper e a API
from scripts.config import DATA_DIR, CSV_FILENAME

def carregar_dados_livros() -> List[Dict[str, Any]]:
    """
    Le o arquivo CSV gerado pelo scraper e retorna como uma lista de dicionarios.
    
    Uso o pandas aqui porque ele e muito eficiente para ler CSV e
    tratar dados, alem de ja estar nos requisitos do projeto.
    
    Retorna:
        Lista de dicionarios contendo os dados dos livros.
        Se o arquivo nao existir, retorna uma lista vazia.
    """
    # Monta o caminho completo do arquivo usando Path para compatibilidade (Vercel/Local)
    base_dir = Path(__file__).resolve().parent.parent
    caminho_csv = base_dir / DATA_DIR / CSV_FILENAME
    
    # Verifica se o arquivo existe antes de tentar ler
    if not os.path.exists(caminho_csv):
        print(f"AVISO: Arquivo {caminho_csv} nao encontrado.")
        return []
    
    try:
        # Le o CSV usando pandas
        df = pd.read_csv(caminho_csv)
        
        # Converte o DataFrame para uma lista de dicionarios (records) para facilitar o retorno em formato JSON pela API
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"ERRO ao ler CSV: {e}")
        return []

# -*- coding: utf-8 -*-
"""
Arquivo de configuracoes do projeto de web scraping.

Aqui centralizamos todas as constantes e parametros que o scraper precisa.
A ideia e que se eu precisar mudar algo (tipo o tempo entre requisicoes ou
a URL base), eu mude so aqui e nao precise ficar procurando no codigo todo.

Autor: Jonathan Cavalcante
RM: 369722
FIAP - Pos Tech Machine Learning Engineering
"""

# =============================================================================
# URLs DO SITE
# =============================================================================

# URL principal do site que vamos fazer scraping
# Esse e um site feito especificamente pra treinar web scraping, entao
# nao tem problema fazer varias requisicoes
BASE_URL = "https://books.toscrape.com"

# URL do catalogo onde ficam os livros
# Uso f-string pra juntar com a BASE_URL
CATALOGUE_URL = f"{BASE_URL}/catalogue"


# =============================================================================
# CONFIGURACOES DE ARQUIVOS
# =============================================================================

# Pasta onde vamos salvar o CSV com os dados
# Criei separado pra manter o projeto organizado
DATA_DIR = "data"

# Nome do arquivo CSV que sera gerado
CSV_FILENAME = "books.csv"


# =============================================================================
# PARAMETROS DO SCRAPING
# =============================================================================

# Tempo de espera entre cada requisicao (em segundos)
# Coloquei 1 segundo pra nao sobrecarregar o servidor, mesmo sendo um site
# de teste. E uma boa pratica em web scraping respeitar o servidor.
DELAY_BETWEEN_REQUESTS = 1

# Tempo maximo de espera por uma resposta do servidor
# Se demorar mais que isso, a requisicao falha e tentamos de novo
REQUEST_TIMEOUT = 10

# Quantas vezes tentamos de novo se der erro numa requisicao
# Coloquei 3 porque as vezes a rede pode oscilar
MAX_RETRIES = 3


# =============================================================================
# MAPEAMENTO DE RATINGS
# =============================================================================

# O site mostra as estrelas como classe CSS (tipo "star-rating Three")
# Entao preciso converter o texto em ingles pro numero correspondente
# Criei esse dicionario pra fazer essa conversao de forma simples
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


# =============================================================================
# HEADERS HTTP
# =============================================================================

# Headers que mandamos junto com a requisicao
# O User-Agent simula um navegador real pra evitar bloqueios
# Alguns sites bloqueiam requisicoes que nao tem User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

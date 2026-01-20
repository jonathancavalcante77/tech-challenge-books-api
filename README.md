# Tech Challenge - Books API

Projeto referente à Fase 1 da Pós-Tech em Machine Learning Engineering (FIAP).
O sistema consiste em um pipeline de dados com Web Scraping, armazenamento em CSV e uma API REST (FastAPI) para consulta e exposição de dados para modelos de Machine Learning.

## Arquitetura

O fluxo de dados segue as etapas:
1. **Scraping**: Extração de dados do site 'Books to Scrape'.
2. **Armazenamento**: Persistência em arquivo CSV local.
3. **API**: Carregamento dos dados em memória e exposição via endpoints REST.
4. **Consumo**: Cliente final ou modelos de ML.

> **Nota:** O arquivo `data/books.csv` está incluído no repositório para facilitar a execução e o deploy. Para regenerar, execute `python scripts/scraper.py`.

## Funcionalidades

- **Core**: Listagem de livros, busca por parâmetros, estatísticas agregadas.
- **Autenticação**: Implementação de JWT (Login e Refresh) para proteção de rotas.
- **Automação**: Endpoint para disparo do processo de scraping e recarga de dados em tempo real.
- **Machine Learning**: Endpoints dedicados para fornecimento de features e dataset de treinamento.

## Instalação e Execução

Pré-requisitos: Python 3.9+

1. Instalar dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Executar a API:
   ```bash
   python -m uvicorn api.main:app --reload
   ```

3. Acessar documentação (Swagger):
   http://127.0.0.1:8000/docs

## Autenticação

Algumas rotas são protegidas e requerem token JWT.

1. **Obter Token**:
   - Rota: `POST /api/v1/auth/login`
   - Body: `{"username": "admin", "password": "secret"}`

2. **Utilizar Token**:
   - Header: `Authorization: Bearer <token>`

## Endpoints Principais

### Públicos
- `GET /api/v1/books`: Listagem paginada.
- `GET /api/v1/books/{id}`: Detalhes do livro.
- `GET /api/v1/stats/overview`: Métricas gerais.

### Protegidos / ML
- `POST /api/v1/scraping/trigger`: Executa scraping e atualiza base de dados.
- `GET /api/v1/ml/features`: Dados formatados para inferência.
- `GET /api/v1/ml/training-data`: Download do CSV completo.
- `POST /api/v1/ml/predictions`: Simulação de inferência de modelo.

## Deploy

O projeto possui configuração para Vercel (`vercel.json`).

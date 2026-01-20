# Tech Challenge Dashboard

Este é um dashboard interativo desenvolvido com **Streamlit** para demonstração visual da API de Livros.
O objetivo é consumir os endpoints públicos da API e apresentar os dados de forma amigável.

## Pré-requisitos

- Python 3.9+
- API (`api.main`) rodando em `http://127.0.0.1:8000` (ou outra URL configurada).

## Instalação

1. Acesse o diretório do projeto.
2. Instale as dependências específicas do dashboard:
   ```bash
   pip install -r dashboard/requirements.txt
   ```

## Execução

1. Certifique-se de que a API principal está rodando em um terminal:
   ```bash
   python -m uvicorn api.main:app --reload
   ```

2. Em **outro terminal**, execute o dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```

3. O navegador abrirá automaticamente em `http://localhost:8501`.

## Configuração

A URL da API pode ser configurada via variável de ambiente `API_BASE_URL`.
Se não definida, o padrão é `http://127.0.0.1:8000`.

**Linux/Mac:**
```bash
export API_BASE_URL="http://seu-servidor-api:8000"
streamlit run dashboard/app.py
```

**Windows (PowerShell):**
```powershell
$env:API_BASE_URL="http://seu-servidor-api:8000"
streamlit run dashboard/app.py
```

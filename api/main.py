
"""
Arquivo principal da API - Tech Challenge Fase 1

Aqui definimos os endpoints da nossa API REST usando FastAPI.
A API le os dados do CSV gerado pelo scraper e expoe para consulta.

Para rodar: uvicorn api.main:app --reload
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import Response
import pandas as pd
import jwt
import datetime
import io
import os

# Importando nossos modulos locais
from .models import Book, StatsOverview, CategoryStats, LoginRequest, Token
from .utils import carregar_dados_livros
from scripts.scraper import run_scraper

# Configurações de Segurança (JWT)
SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me")
ALGORITHM = "HS256"
security = HTTPBearer()


# Criando a instancia da aplicacao FastAPI
app = FastAPI(
    title="Tech Challenge Books API",
    description="API para consulta de livros extraidos do site Books to Scrape.",
    version="1.0.0"
)

# Carregamos os dados na memoria quando a API inicia
LIVROS_DB = carregar_dados_livros()

# Inicializa DataFrame para analises
# Se LIVROS_DB estiver vazio, cria DF vazio com colunas corretas para evitar erros
if LIVROS_DB:
    LIVROS_DF = pd.DataFrame(LIVROS_DB)
else:
    LIVROS_DF = pd.DataFrame(columns=["id", "title", "price", "rating", "availability", "category", "image_url", "product_url"])

# SEGURANÇA E AUTENTICAÇÃO (JWT)

def create_access_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta(hours=1)):
    """Gera um token JWT com tempo de expiração."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verifica se o token JWT é válido."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")

@app.post("/api/v1/auth/login", response_model=Token, summary="Login", description="Autentica usuário e retorna token JWT.")
def login(request: LoginRequest):
    """
    Realiza login (simulado com credenciais hardcoded).
    Usuário: admin
    Senha: admin
    """
    if request.username == "admin" and request.password == "admin":
        token = create_access_token({"sub": request.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.post("/api/v1/auth/refresh", response_model=Token, summary="Renovar Token", description="Gera um novo token JWT válido.")
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Renova o token de acesso.
    Requer um token válido no header Authorization.
    """
    payload = verify_token(credentials)
    # Gera novo token com mais 1h de validade
    new_token = create_access_token({"sub": payload["sub"]})
    return {"access_token": new_token, "token_type": "bearer"}

@app.post("/api/v1/scraping/trigger", summary="Executar Scraping", description="Dispara o processo de scraping e recarrega os dados.")
def trigger_scraping(payload: dict = Depends(verify_token)):
    """
    Endpoint protegido para rodar o scraper sob demanda.
    Requer autenticação JWT.
    
    1. Executa o scraper.py
    2. Recarrega os dados em memória (LIVROS_DB e LIVROS_DF)
    """
    try:
        # Executa o scraper
        run_scraper()
        
        # Recarrega dados
        global LIVROS_DB, LIVROS_DF
        LIVROS_DB = carregar_dados_livros()
        if LIVROS_DB:
            LIVROS_DF = pd.DataFrame(LIVROS_DB)
        else:
            LIVROS_DF = pd.DataFrame(columns=["id", "title", "price", "rating", "availability", "category", "image_url", "product_url"])
            
        return {"status": "success", "message": "Scraping finalizado e dados recarregados.", "total_books": len(LIVROS_DB)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar scraping: {str(e)}")


# ENDPOINTS MACHINE LEARNING


@app.get("/api/v1/ml/features", summary="Obter Features", description="Retorna dados formatados para treinamento de modelos.")
def get_ml_features():
    """
    Retorna os dados dos livros formatados como features numéricas.
    Seleciona: price, rating, availability.
    """
    if LIVROS_DF.empty:
        return []
    
    # Seleciona colunas relevantes para um modelo hipotético
    features = LIVROS_DF[["id", "price", "rating", "availability", "category"]].copy()
    
    # Exemplo de normalização simples (mock)
    return features.to_dict(orient="records")

@app.get("/api/v1/ml/training-data", summary="Download Dataset", description="Baixa o dataset completo em formato CSV.")
def get_training_data():
    """
    Retorna o CSV completo dos livros para ser usado em treinamento.
    """
    if LIVROS_DF.empty:
        raise HTTPException(status_code=404, detail="Sem dados para treinamento.")
        
    stream = io.StringIO()
    LIVROS_DF.to_csv(stream, index=False)
    response = Response(content=stream.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=training_data.csv"
    return response

@app.post("/api/v1/ml/predictions", summary="Simular Predição", description="Recebe dados de um livro e retorna uma categoria prevista (Mock).")
def predict_category(book_features: Dict[str, Any]):
    """
    Simula uma predição de categoria baseada no preço e rating.
    (Mock para fins didáticos).
    """
    price = book_features.get("price", 0)
    rating = book_features.get("rating", 0)
    
    # Lógica "Dummy" de predição
    predicted = "Fiction"
    confidence = 0.85
    
    if price > 50:
        predicted = "Nonfiction"
        confidence = 0.92
    
    if rating == 5:
        confidence = 0.99
        
    return {
        "predicted_category": predicted,
        "confidence": confidence,
        "model_version": "v1.0-mock"
    }


# ENDPOINTS OBRIGATORIOS E INSIGHTS


@app.get("/api/v1/books", response_model=List[Book], summary="Listar Livros", description="Retorna a lista de todos os livros disponíveis com paginação.")
def listar_livros(page: int = Query(1, gt=0), size: int = Query(50, gt=0, le=100)):
    """
    Retorna a lista de livros com paginacao.
    
    Parametros:
    - page: numero da pagina (padrao 1)
    - size: quantidade de itens por pagina (padrao 50, maximo 100)
    
    Fiz a paginacao para nao sobrecarregar a resposta caso tenhamos
    muitos livros no banco de dados.
    """
    # Calculo dos indices para fatiar a lista
    inicio = (page - 1) * size
    fim = inicio + size
    
    # Retorna a fatia da lista correspondente a pagina
    return LIVROS_DB[inicio:fim]


@app.get("/api/v1/books/search", response_model=List[Book], summary="Buscar Livros", description="Pesquisa livros por título ou categoria.")
def buscar_livros(
    title: Optional[str] = None, 
    category: Optional[str] = None
):
    """
    Busca livros por titulo ou categoria.
    
    Parametros:
    - title: parte do titulo do livro (case insensitive)
    - category: nome exato ou parte da categoria
    
    Se nenhum parametro for passado, retorna lista vazia para nao
    trazer o banco todo sem querer.
    """
    # Se nao passar nada, retorna lista vazia
    if not title and not category:
        return []
    
    resultado = []
    
    # Itera sobre todos os livros para filtrar
    for livro in LIVROS_DB:
        match_titulo = True
        match_categoria = True
        
        # Verifica filtro de titulo (se foi passado)
        if title:
            # Converte ambos para minusculo para busca case-insensitive
            if title.lower() not in livro["title"].lower():
                match_titulo = False
        
        # Verifica filtro de categoria (se foi passado)
        if category:
            if category.lower() not in livro["category"].lower():
                match_categoria = False
        
        # Se atendeu a todos os filtros passados, adiciona na lista
        if match_titulo and match_categoria:
            resultado.append(livro)
            
    return resultado


@app.get("/api/v1/stats/overview", response_model=StatsOverview, summary="Estatísticas Gerais", description="Visão geral da coleção: total de livros, média de preços e distribuição de avaliações.")
def obter_resumo_estatistico():
    """
    Retorna estatisticas gerais da colecao de livros.
    
    Conforme documentacao:
    - total de livros
    - preco medio
    - distribuicao de ratings
    """
    if LIVROS_DF.empty:
        return {
            "total_books": 0,
            "average_price": 0.0,
            "min_price": 0.0,
            "max_price": 0.0,
            "rating_distribution": {},
            "categories_count": 0
        }
    
    # Calculando distribuicao de ratings
    # Convertendo chaves para string para garantir compatibilidade JSON
    rating_counts = LIVROS_DF["rating"].value_counts().to_dict()
    rating_dist = {str(k): v for k, v in rating_counts.items()}
    
    return {
        "total_books": int(len(LIVROS_DF)),
        "average_price": round(float(LIVROS_DF["price"].mean()), 2),
        "min_price": float(LIVROS_DF["price"].min()),
        "max_price": float(LIVROS_DF["price"].max()),
        "rating_distribution": rating_dist,
        "categories_count": int(LIVROS_DF["category"].nunique())
    }


@app.get("/api/v1/stats/categories", response_model=List[CategoryStats], summary="Estatísticas por Categoria", description="Dados detalhados agrupados por categoria (total, preços).")
def obter_estatisticas_por_categoria():
    """
    Retorna estatisticas detalhadas por categoria.
    Ordenado por quantidade de livros (decrescente).
    """
    if LIVROS_DF.empty:
        return []
        
    # Agrupando por categoria e calculando metricas
    stats = LIVROS_DF.groupby("category").agg(
        total_books=("id", "count"),
        average_price=("price", "mean"),
        min_price=("price", "min"),
        max_price=("price", "max")
    ).reset_index()
    
    # Ordenacao: Quantidade desc, Categoria asc (desempate)
    stats = stats.sort_values(by=["total_books", "category"], ascending=[False, True])
    
    # Convertendo para lista de dicionarios
    result = stats.to_dict(orient="records")
    
    # Arredondando valores float
    for item in result:
        item["average_price"] = round(item["average_price"], 2)
        
    return result


@app.get("/api/v1/books/top-rated", response_model=List[Book], summary="Melhores Avaliados", description="Lista os livros com maior classificação (5 estrelas), ordenados por preço.")
def obter_melhores_livros(limit: int = Query(10, gt=0, le=50)):
    """
    Lista os livros com melhor avaliacao.
    
    Criterios de ordenacao:
    1. Rating (maior para menor)
    2. Price (maior para menor)
    3. Title (alfabetico - desempate)
    """
    if LIVROS_DF.empty:
        return []
        
    top_books = LIVROS_DF.sort_values(
        by=["rating", "price", "title"], 
        ascending=[False, False, True]
    ).head(limit)
    
    return top_books.to_dict(orient="records")


@app.get("/api/v1/books/price-range", response_model=List[Book], summary="Filtrar por Faixa de Preço", description="Filtra livros dentro de um intervalo de preço (min e max).")
def filtrar_livros_por_preco(
    min: float = Query(0.0, ge=0.0, description="Preco minimo"),
    max: float = Query(99999.0, ge=0.0, description="Preco maximo")
):
    """
    Filtra livros dentro de uma faixa de preco especifica.
    
    Parametros nomeados 'min' e 'max'.
    """
    if LIVROS_DF.empty:
        return []
    
    if min > max:
        raise HTTPException(status_code=400, detail="O valor minimo (min) nao pode ser maior que o maximo (max).")
        
    # Aplicando filtro
    filtered_books = LIVROS_DF[
        (LIVROS_DF["price"] >= min) & 
        (LIVROS_DF["price"] <= max)
    ]
    
    # Ordenacao por preco (crescente)
    filtered_books = filtered_books.sort_values(by=["price", "title"], ascending=[True, True])
    
    return filtered_books.to_dict(orient="records")


@app.get("/api/v1/books/{book_id}", response_model=Book, summary="Detalhar Livro", description="Retorna todos os detalhes de um livro específico pelo ID.")
def obter_detalhes_livro(book_id: int):
    """
    Retorna os detalhes de um livro especifico pelo ID.
    
    Se o livro nao for encontrado, retorna erro 404.
    """
    # Procura o livro na lista pelo ID
    for livro in LIVROS_DB:
        if livro["id"] == book_id:
            return livro
            
    # Se terminou o loop e nao achou, levanta excecao HTTP
    raise HTTPException(status_code=404, detail="Livro nao encontrado")


@app.get("/api/v1/categories", response_model=List[str], summary="Listar Categorias", description="Lista todas as categorias únicas disponíveis no banco de dados.")
def listar_categorias():
    """
    Retorna uma lista unica de todas as categorias disponiveis.
    """
    # Usa um set (conjunto) para pegar apenas valores unicos
    categorias = set()
    for livro in LIVROS_DB:
        categorias.add(livro["category"])
    
    # Converte de volta para lista e ordena alfabeticamente
    return sorted(list(categorias))


@app.get("/api/v1/health", summary="Status da API", description="Verifica a saúde do serviço e contagem de dados carregados.")
def verificar_status_api():
    """
    Endpoint para verificar a saude da API.
    
    Retorna o status e quantos livros estao carregados na memoria.
    Util para monitoramento.
    """
    return {
        "status": "ok",
        "api_name": "Tech Challenge Books API",
        "total_books_loaded": len(LIVROS_DB)
    }

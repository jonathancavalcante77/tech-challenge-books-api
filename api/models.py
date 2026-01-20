"""
Modelos de dados da API (Pydantic).

Aqui definimos a estrutura dos dados que nossa API vai retornar.
O Pydantic ajuda a validar os tipos de dados e gera a documentacao
automatica no Swagger UI.
"""

from typing import Optional, Dict
from pydantic import BaseModel

class StatsOverview(BaseModel):
    """
    Modelo para estatisticas gerais da colecao.
    """
    total_books: int
    average_price: float
    min_price: float
    max_price: float
    rating_distribution: Dict[str, int]  # Chaves como string para JSON (ex: "5 estrelas")
    categories_count: int

class CategoryStats(BaseModel):
    """
    Modelo para estatisticas por categoria.
    """
    category: str
    total_books: int
    average_price: float
    min_price: float
    max_price: float

class LoginRequest(BaseModel):
    """
    Modelo para requisicao de login.
    """
    username: str
    password: str

class Token(BaseModel):
    """
    Modelo de resposta do token JWT.
    """
    access_token: str
    token_type: str

class Book(BaseModel):
    """
    Modelo que representa um livro na nossa API.
    
    Os campos devem bater com o que temos no arquivo books.csv
    gerado pelo scraper.
    """
    id: int
    title: str
    price: float
    rating: int
    availability: int
    category: str
    image_url: str
    product_url: str

    # Configurações extras para documentação
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "A Light in the Attic",
                "price": 51.77,
                "rating": 3,
                "availability": 22,
                "category": "Poetry",
                "image_url": "http://books.toscrape.com/media/cache/...",
                "product_url": "http://books.toscrape.com/catalogue/..."
            }
        }
    }

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import datetime

# Configuração da Página
st.set_page_config(
    page_title="Tech Challenge - Books Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração da URL da API
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")

def fetch_api(endpoint, params=None):
    """
    Função auxiliar para consumir a API.
    Retorna o JSON da resposta ou None em caso de erro.
    """
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Erro de Conexão: Não foi possível conectar a {url}. Verifique se a API está rodando.")
        return None
    except requests.exceptions.Timeout:
        st.error(f"Timeout: A requisição para {url} demorou muito.")
        return None
    except requests.exceptions.HTTPError as err:
        st.error(f"Erro HTTP {err.response.status_code}: {err}")
        return None
    except Exception as e:
        st.error(f"Erro desconhecido: {e}")
        return None

def render_status():
    st.header("Status do Sistema")
    
    st.info(f"Conectado a: {API_BASE_URL}")
    st.text(f"Última atualização: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    if st.button("Verificar Status"):
        data = fetch_api("/api/v1/health")
        if data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Status API", data.get("status", "Unknown"))
            with col2:
                st.metric("Total de Livros Carregados", data.get("total_books_loaded", 0))
            
            st.json(data)

def render_overview():
    st.header("Visão Geral da Coleção")
    
    data = fetch_api("/api/v1/stats/overview")
    if data:
        # Métricas Principais
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Livros", data.get("total_books"))
        col2.metric("Preço Médio", f"£ {data.get('average_price')}")
        col3.metric("Menor Preço", f"£ {data.get('min_price')}")
        col4.metric("Maior Preço", f"£ {data.get('max_price')}")
        
        st.subheader("Distribuição de Avaliações")
        rating_dist = data.get("rating_distribution", {})
        
        # Converter para DataFrame para melhor visualização
        if rating_dist:
            df_rating = pd.DataFrame(list(rating_dist.items()), columns=["Estrelas", "Quantidade"])
            df_rating["Estrelas"] = df_rating["Estrelas"].astype(str) + " Estrelas"
            
            # Gráfico Simples
            fig = px.bar(
                df_rating, 
                x="Estrelas", 
                y="Quantidade", 
                title="Quantidade de Livros por Avaliação",
                text_auto=True
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela
            st.dataframe(df_rating, hide_index=True)

def render_categories():
    st.header("Análise por Categorias")
    
    data = fetch_api("/api/v1/stats/categories")
    if data:
        df = pd.DataFrame(data)
        
        # Renomear colunas para exibição
        df_display = df.rename(columns={
            "category": "Categoria",
            "total_books": "Qtd. Livros",
            "average_price": "Preço Médio (£)",
            "min_price": "Mínimo (£)",
            "max_price": "Máximo (£)"
        })
        
        st.subheader("Top 10 Categorias (Por Quantidade)")
        top_10 = df.sort_values("total_books", ascending=False).head(10)
        
        fig = px.bar(
            top_10, 
            x="category", 
            y="total_books", 
            color="average_price",
            labels={"category": "Categoria", "total_books": "Quantidade", "average_price": "Preço Médio"},
            title="Categorias com mais livros",
            text="total_books"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Dados Detalhados")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

def render_search():
    st.header("Buscar Livros")
    
    col1, col2 = st.columns(2)
    with col1:
        title_query = st.text_input("Título (parcial)")
    with col2:
        cat_query = st.text_input("Categoria (parcial)")
        
    if st.button("Pesquisar"):
        params = {}
        if title_query:
            params["title"] = title_query
        if cat_query:
            params["category"] = cat_query
            
        data = fetch_api("/api/v1/books/search", params=params)
        
        if data:
            st.success(f"Encontrados {len(data)} resultados.")
            df = pd.DataFrame(data)
            
            # Selecionar colunas principais
            if not df.empty:
                cols = ["id", "title", "category", "price", "rating", "availability"]
                st.dataframe(df[cols], use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum livro encontrado com esses filtros.")
        elif data == []:
             st.warning("Nenhum livro encontrado.")

def render_top_rated():
    st.header("Top Rated Books")
    
    limit = st.slider("Quantidade de livros", min_value=5, max_value=50, value=10)
    
    if st.button("Carregar Lista"):
        data = fetch_api("/api/v1/books/top-rated", params={"limit": limit})
        if data:
            df = pd.DataFrame(data)
            if not df.empty:
                st.dataframe(
                    df[["title", "rating", "price", "category", "availability"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhum dado retornado.")

# Menu Principal
def main():
    st.sidebar.title("Tech Challenge")
    st.sidebar.caption("Dashboard de Demonstração")
    
    options = ["Status", "Visão Geral", "Categorias", "Busca", "Top Rated"]
    choice = st.sidebar.radio("Navegação", options)
    
    if choice == "Status":
        render_status()
    elif choice == "Visão Geral":
        render_overview()
    elif choice == "Categorias":
        render_categories()
    elif choice == "Busca":
        render_search()
    elif choice == "Top Rated":
        render_top_rated()

if __name__ == "__main__":
    main()

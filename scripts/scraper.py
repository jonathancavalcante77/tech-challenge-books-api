# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
from scripts.config import BASE_URL, DATA_DIR, CSV_FILENAME, RATING_MAP, HEADERS

def get_soup(url):
    """
    Faz a requisição HTTP e retorna o objeto BeautifulSoup.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def extract_book_data(article, category_name):
    """
    Extrai os dados de um livro a partir do elemento HTML (article).
    """
    try:
        # Título
        h3 = article.find('h3')
        title = h3.find('a')['title']
        
        # URL do Produto
        relative_url = h3.find('a')['href']
        # Tratar URLs relativas corretamente
        if "catalogue/" in relative_url:
             product_url = BASE_URL + "/" + relative_url
        else:
             # Limpar caminho relativo
             clean_rel = relative_url.replace("../", "")
             product_url = BASE_URL + "/catalogue/" + clean_rel

        # URL da Imagem
        img_relative = article.find('img')['src']
        image_url = BASE_URL + img_relative.replace("../..", "")
        
        # Avaliação (Rating)
        star_tag = article.find('p', class_='star-rating')
        rating_class = star_tag['class'][1] 
        rating = RATING_MAP.get(rating_class, 0)
        
        # Preço
        price_text = article.find('p', class_='price_color').text
        price = float(price_text.replace('£', ''))
        
        # Disponibilidade (Simplificado: 1 se "In stock" estiver presente)
        instock = article.find('p', class_='instock availability')
        availability = 1 if instock and "In stock" in instock.text else 0
        
        return {
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "category": category_name,
            "image_url": image_url,
            "product_url": product_url
        }
    except Exception as e:
        print(f"Erro ao extrair livro: {e}")
        return None

def run_scraper():
    """
    Função principal que executa todo o processo de scraping.
    Navega por categorias e paginação.
    """
    print("Iniciando Scraping...")
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    books = []
    id_counter = 1
    
    # 1. Obter Categorias da Página Inicial
    soup = get_soup(BASE_URL + "/index.html")
    if not soup: return
    
    side_cats = soup.select('.side_categories ul li ul li a')
    categories = []
    for cat in side_cats:
        cat_name = cat.text.strip()
        cat_url = BASE_URL + "/" + cat['href']
        categories.append((cat_name, cat_url))
        
    print(f"Encontradas {len(categories)} categorias.")
    
    for cat_name, cat_url in categories:
        current_url = cat_url
        
        while True:
            cat_soup = get_soup(current_url)
            if not cat_soup: break
            
            articles = cat_soup.find_all('article', class_='product_pod')
            for article in articles:
                book_data = extract_book_data(article, cat_name)
                if book_data:
                    book_data['id'] = id_counter
                    books.append(book_data)
                    id_counter += 1
            
            # Paginação (Próxima Página)
            next_li = cat_soup.find('li', class_='next')
            if next_li:
                next_url = next_li.find('a')['href']
                parent = current_url.rsplit('/', 1)[0]
                current_url = parent + "/" + next_url
            else:
                break
                
    # Salvar em CSV
    df = pd.DataFrame(books)
    cols = ['id', 'title', 'price', 'rating', 'availability', 'category', 'image_url', 'product_url']
    if not df.empty:
        df = df[cols]
    
    csv_path = os.path.join(DATA_DIR, CSV_FILENAME)
    df.to_csv(csv_path, index=False)
    print(f"SCRAPING FINALIZADO - Total {len(df)} livros salvos em {csv_path}")

if __name__ == "__main__":
    run_scraper()

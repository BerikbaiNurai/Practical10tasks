from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

PRODUCTS_DB = [
    {"id": 1, "name": "Смартфон Alpha", "category": "Электроника", "price": 550},
    {"id": 2, "name": "Ноутбук ProBook", "category": "Электроника", "price": 1200},
    {"id": 3, "name": "Беспроводные наушники SoundWave", "category": "Электроника", "price": 150},
    {"id": 4, "name": "Футболка 'Код'", "category": "Одежда", "price": 25},
    {"id": 5, "name": "Джинсы 'Классика'", "category": "Одежда", "price": 75},
    {"id": 6, "name": "Книга 'Паттерны проектирования'", "category": "Книги", "price": 40},
    {"id": 7, "name": "Книга 'Чистый код'", "category": "Книги", "price": 35},
    {"id": 8, "name": "Умные часы Chronos", "category": "Электроника", "price": 300},
    {"id": 9, "name": "Худи 'Логотип'", "category": "Одежда", "price": 60},
]

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float

@app.get("/api/products", response_model=List[Product])
async def filter_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_price: Optional[str] = Query(None),
    max_price: Optional[str] = Query(None),
    sort: Optional[str] = Query(None)
):
    filtered_products = PRODUCTS_DB.copy()

    if category and category.lower() != "all":
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]

    if search:
        filtered_products = [p for p in filtered_products if search.lower() in p["name"].lower()]

    try:
        if min_price and min_price != "":
            min_price_val = float(min_price)
            filtered_products = [p for p in filtered_products if p["price"] >= min_price_val]
        if max_price and max_price != "":
            max_price_val = float(max_price)
            filtered_products = [p for p in filtered_products if p["price"] <= max_price_val]
    except ValueError:
        pass  

    if sort == "price_asc":
        filtered_products.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        filtered_products.sort(key=lambda x: x["price"], reverse=True)

    return filtered_products

@app.get("/api/categories", response_model=List[str])
async def get_categories():
    """Возвращает список уникальных категорий."""
    categories = sorted(list(set(p["category"] for p in PRODUCTS_DB)))
    return categories
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
print("🔑 OPENWEATHER_API_KEY =", os.getenv("OPENWEATHER_API_KEY"))

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

@app.get("/api/weather/{city}")
async def get_weather(city: str):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key is not configured")

    url = f"{BASE_URL}/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="City not found")
    if response.status_code != 200:
        error_detail = response.json().get("message", "Error fetching weather data")
        raise HTTPException(status_code=response.status_code, detail=error_detail)

    data = response.json()

    return {
        "city_name": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }

@app.get("/api/forecast/{city}")
async def get_forecast(city: str):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key is not configured")

    url = f"{BASE_URL}/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        error_detail = response.json().get("message", "Error fetching forecast")
        raise HTTPException(status_code=response.status_code, detail=error_detail)

    data = response.json()

    daily_forecast = data["list"][::8]

    result = []
    for item in daily_forecast:
        result.append({
            "datetime": item["dt_txt"],
            "temp": item["main"]["temp"],
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"]
        })

    return result

@app.get("/api/weather/coords/")
async def get_weather_by_coords(lat: float, lon: float):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key is not configured")

    url = f"{BASE_URL}/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        error_detail = response.json().get("message", "Error fetching weather by coords")
        raise HTTPException(status_code=response.status_code, detail=error_detail)

    data = response.json()

    return {
        "city_name": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }

@app.get("/")
def root():
    return {"message": "FastAPI backend is running 🚀"}

print("\n📌 Список маршрутов:")
for route in app.routes:
    print("🔗", route.path)
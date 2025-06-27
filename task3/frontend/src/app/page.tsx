'use client';

import { useState, useEffect, FormEvent } from 'react';
import axios from 'axios';
import Image from 'next/image';

interface WeatherData {
  city_name: string;
  temperature: number;
  description: string;
  icon: string;
}

interface ForecastItem {
  datetime: string;
  temperature: number;
  description: string;
}

const API_BASE_URL = 'http://localhost:8000/api';

export default function Home() {
  const [city, setCity] = useState('Almaty');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<ForecastItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchWeather = async (cityName: string) => {
    setLoading(true);
    setError('');
    setWeather(null);
    setForecast([]);

    try {
      const res = await axios.get(`${API_BASE_URL}/weather/${cityName}`);
      setWeather(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки погоды.');
    } finally {
      setLoading(false);
    }
  };

  const fetchForecast = async (cityName: string) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/forecast/${cityName}`);
      setForecast(res.data);
    } catch (err) {
      console.error('Ошибка прогноза:', err);
    }
  };

  useEffect(() => {
    fetchWeather(city);
  }, []);

  useEffect(() => {
    if (weather?.city_name) {
      fetchForecast(weather.city_name);
    }
  }, [weather?.city_name]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (city.trim()) {
      fetchWeather(city.trim());
    }
  };

  const handleGeolocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        const { latitude, longitude } = position.coords;
        setLoading(true);
        setError('');
        setWeather(null);
        setForecast([]);

        try {
          const res = await axios.get(`${API_BASE_URL}/weather/coords/`, {  // добавлен слэш
            params: { lat: latitude, lon: longitude },
          });
          setWeather(res.data);
        } catch (err: any) {
          setError('Ошибка получения погоды по геолокации.');
        } finally {
          setLoading(false);
        }
      });
    } else {
      setError('Геолокация не поддерживается вашим браузером.');
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-200 to-purple-300 p-4">
      <div className="w-full max-w-sm bg-white/50 backdrop-blur-md p-6 rounded-2xl shadow-lg">
        <h1 className="text-2xl font-bold text-gray-800 mb-4 text-center">Погода</h1>

        {/* Кнопка Геолокации */}
        <button
          onClick={handleGeolocation}
          className="mb-4 w-full bg-green-500 hover:bg-green-600 text-white font-bold p-2 rounded-lg"
        >
          Показать погоду по моему местоположению
        </button>

        {/* Форма ввода города */}
        <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Введите город"
            className="flex-grow p-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold p-2 rounded-lg disabled:bg-blue-300"
          >
            {loading ? '...' : '➔'}
          </button>
        </form>

        {/* Сообщения об ошибках и загрузке */}
        {loading && <p className="text-center text-gray-700">Загрузка...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}

        {/* Погода */}
        {weather && (
          <div className="flex flex-col items-center text-center text-gray-900">
            <h2 className="text-3xl font-semibold">{weather.city_name}</h2>
            <div className="flex items-center">
              <p className="text-6xl font-light">{Math.round(weather.temperature)}°C</p>
              <Image
                src={`https://openweathermap.org/img/wn/${weather.icon}@2x.png`}
                alt={weather.description}
                width={100}
                height={100}
              />
            </div>
            <p className="text-lg capitalize">{weather.description}</p>
          </div>
        )}

        {/* Прогноз на 5 дней */}
        {forecast.length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-bold mb-2">Прогноз на 5 дней:</h3>
            <ul className="space-y-1 text-sm text-gray-800">
              {forecast.map((item, index) => (
                <li key={index}>
                  {item.datetime}: {Math.round(item.temperature)}°C, {item.description}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </main>
  );
}
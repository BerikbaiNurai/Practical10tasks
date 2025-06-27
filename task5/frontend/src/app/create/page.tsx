"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export default function CreatePollPage() {
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState(['', '']);
  const router = useRouter();

  const handleOptionChange = (value: string, index: number) => {
    const newOptions = [...options];
    newOptions[index] = value;
    setOptions(newOptions);
  };

  const addOption = () => setOptions([...options, '']);
  const removeOption = (index: number) => {
    if (options.length <= 2) return;
    const newOptions = [...options];
    newOptions.splice(index, 1);
    setOptions(newOptions);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/poll/create`, {
        question,
        options,
      });
      router.push('/');
    } catch (error) {
      console.error("Ошибка при создании опроса:", error);
    }
  };

  return (
    <main className="flex items-center justify-center min-h-screen bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-xl p-6 bg-white rounded-xl shadow-lg space-y-4"
      >
        <h2 className="text-xl font-bold text-center">Создать опрос</h2>
        <input
          type="text"
          placeholder="Введите вопрос"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          required
          className="w-full border p-2 rounded"
        />
        <div className="space-y-2">
          {options.map((opt, idx) => (
            <div key={idx} className="flex gap-2">
              <input
                type="text"
                value={opt}
                placeholder={`Вариант ${idx + 1}`}
                onChange={(e) => handleOptionChange(e.target.value, idx)}
                required
                className="flex-1 border p-2 rounded"
              />
              {options.length > 2 && (
                <button
                  type="button"
                  onClick={() => removeOption(idx)}
                  className="px-3 text-red-600 font-bold"
                >
                  ×
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addOption}
            className="text-blue-600 hover:underline"
          >
            + Добавить вариант
          </button>
        </div>
        <button
          type="submit"
          className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded font-semibold"
        >
          Создать опрос
        </button>
      </form>
    </main>
  );
}

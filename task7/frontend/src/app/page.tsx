'use client';

import { useState, useEffect, FormEvent } from 'react';
import axios from 'axios';

interface Entry {
  id: string;
  name: string;
  message: string;
  timestamp: string;
}

const API_URL = 'http://localhost:8000/api/entries';

export default function Home() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [page, setPage] = useState(1);
  const limit = 3;

  const fetchEntries = async () => {
    try {
      const res = await axios.get(`${API_URL}?page=${page}&limit=${limit}`);
      const sorted = res.data.sort((a: Entry, b: Entry) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );
      setEntries(sorted);
    } catch {
      setError('Не удалось загрузить записи.');
    }
  };

  useEffect(() => {
    fetchEntries();
  }, [page]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const trimmedName = name.trim();
    const trimmedMessage = message.trim();

    if (!trimmedName || !trimmedMessage) {
      setError('Имя и сообщение не могут быть пустыми.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await axios.post(API_URL, { name: trimmedName, message: trimmedMessage });
      setName('');
      setMessage('');
      setPage(1);
      fetchEntries();
    } catch (err: any) {
      console.error('Ошибка при отправке:', err.response?.data || err.message);
      setError('Ошибка при отправке сообщения.');
    } finally {
      setLoading(false);
    }
  };

  const deleteEntry = async (id: string) => {
    await axios.delete(`${API_URL}/${id}`);
    fetchEntries();
  };

  const startEdit = (entry: Entry) => {
    setEditingId(entry.id);
    setEditText(entry.message);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditText('');
  };

  const saveEdit = async (id: string) => {
    await axios.put(`${API_URL}/${id}`, { message: editText.trim() });
    setEditingId(null);
    fetchEntries();
  };

  return (
    <main className="bg-gray-100 min-h-screen p-4 sm:p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">Гостевая Книга</h1>

        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-2xl font-semibold mb-4">Оставить запись</h2>
          {error && <p className="text-red-500 mb-4">{error}</p>}
          <div className="mb-4">
            <label className="block text-gray-700 mb-1">Ваше имя</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="Аноним"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 mb-1">Сообщение</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              rows={3}
              placeholder="Всем привет!"
            ></textarea>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300"
          >
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>

        <div className="space-y-4">
          {entries.map((entry) => (
            <div key={entry.id} className="bg-white p-4 rounded-lg shadow">
              {editingId === entry.id ? (
                <>
                  <textarea
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md mb-2"
                  />
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={() => saveEdit(entry.id)}
                      className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                    >
                      Сохранить
                    </button>
                    <button
                      onClick={cancelEdit}
                      className="bg-gray-300 px-3 py-1 rounded hover:bg-gray-400"
                    >
                      Отмена
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <p className="text-gray-800">{entry.message}</p>
                  <div className="text-right text-sm text-gray-500 mt-2">
                    <strong>- {entry.name}</strong> в{' '}
                    {new Date(entry.timestamp).toLocaleString()}
                  </div>
                  <div className="flex justify-end space-x-2 mt-2">
                    <button
                      onClick={() => startEdit(entry)}
                      className="text-blue-500 hover:underline"
                    >
                      Редактировать
                    </button>
                    <button
                      onClick={() => deleteEntry(entry.id)}
                      className="text-red-500 hover:underline"
                    >
                      Удалить
                    </button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-between mt-8">
          <button
            onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
            disabled={page === 1}
            className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400 disabled:opacity-50"
          >
            ← Назад
          </button>
          <button
            onClick={() => setPage((prev) => prev + 1)}
            className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
          >
            Вперед →
          </button>
        </div>
      </div>
    </main>
  );
}
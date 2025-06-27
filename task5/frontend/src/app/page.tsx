"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface PollOption {
  label: string;
  votes: number;
}
interface PollData {
  id: string;
  question: string;
  options: Record<string, PollOption>;
}

const API_URL = 'http://localhost:8000/api';

export default function Home() {
  const [pollData, setPollData] = useState<PollData | null>(null);
  const [voted, setVoted] = useState<string | null>(null);

  const fetchPollData = async () => {
    try {
      const response = await axios.get(`${API_URL}/poll/latest`);
      const poll = response.data;
      setPollData(poll);
      const saved = localStorage.getItem(`poll-vote-${poll.id}`);
      if (saved) setVoted(saved);
    } catch (error) {
      console.error("Ошибка загрузки:", error);
    }
  };

  useEffect(() => {
    fetchPollData();
    const interval = setInterval(fetchPollData, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleVote = async (optionKey: string) => {
    if (!pollData || voted) return;
    try {
      const response = await axios.post(`${API_URL}/poll/vote/${pollData.id}/${optionKey}`);
      setPollData(response.data);
      setVoted(optionKey);
      localStorage.setItem(`poll-vote-${pollData.id}`, optionKey);
    } catch (error) {
      console.error("Ошибка голосования:", error);
    }
  };

  const totalVotes = pollData
    ? Object.values(pollData.options).reduce((sum, o) => sum + o.votes, 0)
    : 0;

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-2xl w-full p-6 bg-white shadow-lg rounded-xl space-y-6">
        {pollData ? (
          <>
            <h1 className="text-2xl font-bold text-center">{pollData.question}</h1>
            {Object.entries(pollData.options).map(([key, option]) => {
              const percent = totalVotes > 0 ? (option.votes / totalVotes) * 100 : 0;
              return (
                <div key={key}>
                  <div className="flex justify-between">
                    <span>{option.label}</span>
                    <span className="text-sm text-gray-500">{option.votes} ({percent.toFixed(1)}%)</span>
                  </div>
                  <div className="w-full h-6 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 transition-all text-white text-xs px-2 flex items-center"
                      style={{ width: `${percent}%` }}
                    ></div>
                  </div>
                  <button
                    disabled={!!voted}
                    onClick={() => handleVote(key)}
                    className={`w-full mt-1 py-1 text-white rounded ${
                      voted ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'
                    } ${voted === key ? '!bg-blue-700' : ''}`}
                  >
                    {voted === key ? 'Ваш голос' : 'Голосовать'}
                  </button>
                </div>
              );
            })}
            <div className="text-center pt-4 border-t font-medium text-gray-600">
              Всего голосов: {totalVotes}
            </div>
            <div className="text-center pt-2">
              <Link href="/create" className="text-blue-600 hover:underline">Создать новый опрос</Link>
            </div>
          </>
        ) : (
          <p>Загрузка опроса...</p>
        )}
      </div>
    </main>
  );
}

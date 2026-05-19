import { useEffect, useState } from 'react';

export default function Home() {
  const [message, setMessage] = useState('Loading...');

  useEffect(() => {
    fetch(process.env.NEXT_PUBLIC_API_URL + '/api/ping')
      .then((response) => response.json())
      .then((data) => setMessage(data.message || 'No response'))
      .catch(() => setMessage('Unable to reach backend'));
  }, []);

  return (
    <main className="min-h-screen bg-base-200 flex items-center justify-center p-6">
      <div className="card w-full max-w-md bg-base-100 shadow-xl">
        <div className="card-body">
          <h1 className="card-title">Fire Spread Prediction</h1>
          <p>Backend response: {message}</p>
          <p>
            API endpoint: <code className="text-xs">{process.env.NEXT_PUBLIC_API_URL}</code>
          </p>
          <div className="card-actions justify-end">
            <button className="btn btn-primary" type="button">
              Refresh
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}

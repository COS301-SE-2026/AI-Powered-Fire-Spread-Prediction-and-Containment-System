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
    <main style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'sans-serif'}}>
      <div style={{textAlign: 'center'}}>
        <h1>Fire Spread Prediction</h1>
        <p>Backend response: {message}</p>
        <p>API endpoint: <code>{process.env.NEXT_PUBLIC_API_URL}</code></p>
      </div>
    </main>
  );
}

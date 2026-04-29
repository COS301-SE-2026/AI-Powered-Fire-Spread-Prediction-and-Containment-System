const axios = require('axios');

const baseUrl = process.env.BACKEND_URL || 'http://localhost:8000';

describe('Backend E2E', () => {
  it('responds to /api/ping', async () => {
    const response = await axios.get(`${baseUrl}/api/ping`);
    expect(response.status).toBe(200);
    expect(response.data).toEqual({ message: 'pong' });
  });

  it('responds to /health', async () => {
    const response = await axios.get(`${baseUrl}/health`);
    expect(response.status).toBe(200);
    expect(response.data).toMatchObject({
      status: 'ok',
      db_host: expect.any(String),
    });
  });
});

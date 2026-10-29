import { describe, it, expect } from 'vitest';
import request from 'supertest';
import { app } from '../src/app.js';

describe('HTTP Server Endpoints', () => {
  it('GET /brokers returns the BR broker pack', async () => {
    const response = await request(app).get('/brokers');

    expect(response.status).toBe(200);
    expect(response.body.pack).toBe('BR');
    expect(response.body.total).toBe(5);
    expect(response.body.validators).toEqual(['CPF', 'CNPJ', 'Serpro', 'ReceitaWS']);

    const brokerIds = response.body.brokers.map((b: { id: string }) => b.id);
    expect(brokerIds).toEqual(['listatelefonica', 'apontador', 'guiamais', 'telelistas', '118']);
  });

  it('GET /health returns health status', async () => {
    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('ok');
    expect(response.body.timestamp).toBeDefined();
  });
});

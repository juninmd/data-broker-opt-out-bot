import express, { Request, Response } from 'express';
import { defaultRegistry } from './brokers/registry.js';

export const app = express();

app.use(express.json());

app.get('/brokers', (req: Request, res: Response) => {
  const brBrokers = defaultRegistry.getBrazilianPack();

  res.json({
    pack: 'BR',
    total: brBrokers.length,
    validators: ['CPF', 'CNPJ', 'Serpro', 'ReceitaWS'],
    brokers: brBrokers.map(adapter => adapter.info)
  });
});

app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
import { defaultRegistry } from '../src/brokers/registry.js';
import { ListaTelefonicaAdapter } from '../src/brokers/adapters/listatelefonica.js';
import { ApontadorAdapter } from '../src/brokers/adapters/apontador.js';
import { GuiaMaisAdapter } from '../src/brokers/adapters/guiamais.js';
import { TeleListasAdapter } from '../src/brokers/adapters/telelistas.js';
import { Broker118Adapter } from '../src/brokers/adapters/broker118.js';

describe('Broker Adapters and Fixtures', () => {
  const brokers = [
    { id: 'listatelefonica', adapter: new ListaTelefonicaAdapter() },
    { id: 'apontador', adapter: new ApontadorAdapter() },
    { id: 'guiamais', adapter: new GuiaMaisAdapter() },
    { id: 'telelistas', adapter: new TeleListasAdapter() },
    { id: '118', adapter: new Broker118Adapter() }
  ];

  const validCPF = '52998224725';
  const invalidCPF = '12345678900';

  for (const { id, adapter } of brokers) {
    describe(`Broker: ${id}`, () => {
      const fixtureDir = path.join(process.cwd(), 'fixtures', 'brokers', id);

      it('has 3 fixture files created', () => {
        expect(fs.existsSync(fixtureDir)).toBe(true);
        const files = fs.readdirSync(fixtureDir);
        expect(files.length).toBeGreaterThanOrEqual(3);
        expect(files).toContain('search_found.html');
        expect(files).toContain('optout_success.html');
        expect(files).toContain('optout_error.html');
      });

      it('rejects opt-out request when CPF/CNPJ checksum is invalid', async () => {
        const response = await adapter.processOptOut({
          fullName: 'Test User',
          document: invalidCPF,
          email: 'test@example.com'
        });

        expect(response.success).toBe(false);
        expect(response.message).toContain('Invalid CPF or CNPJ checksum');
      });

      it('processes opt-out successfully with valid document and success fixture', async () => {
        const successFixture = fs.readFileSync(path.join(fixtureDir, 'optout_success.html'), 'utf-8');
        const response = await adapter.processOptOut(
          {
            fullName: 'Test User',
            document: validCPF,
            email: 'test@example.com'
          },
          successFixture
        );

        expect(response.success).toBe(true);
        expect(response.brokerId).toBe(id);
        expect(response.requestId).toBeDefined();
      });

      it('parses error fixture correctly', async () => {
        const errorFixture = fs.readFileSync(path.join(fixtureDir, 'optout_error.html'), 'utf-8');
        const parsed = adapter.parseFixture(errorFixture);

        expect(parsed.success).toBe(false);
      });

      it('parses search found fixture correctly', async () => {
        const searchFixture = fs.readFileSync(path.join(fixtureDir, 'search_found.html'), 'utf-8');
        const parsed = adapter.parseFixture(searchFixture);

        expect(parsed.status).toBe('PROFILE_FOUND');
      });
    });
  }

  it('registry includes all 5 Brazilian brokers in BR pack', () => {
    const brPack = defaultRegistry.getBrazilianPack();
    expect(brPack.length).toBe(5);
    const ids = brPack.map(b => b.info.id);
    expect(ids).toContain('listatelefonica');
    expect(ids).toContain('apontador');
    expect(ids).toContain('guiamais');
    expect(ids).toContain('telelistas');
    expect(ids).toContain('118');
  });
});

import { describe, it, expect, vi } from 'vitest';
import { isValidCPF, formatCPF } from '../src/validators/cpf.js';
import { isValidCNPJ, formatCNPJ } from '../src/validators/cnpj.js';
import { SerproValidator } from '../src/validators/serpro.js';
import { ReceitaWSValidator } from '../src/validators/receitaws.js';

describe('CPF Validator', () => {
  it('rejects invalid checksums and invalid lengths', () => {
    expect(isValidCPF('111.111.111-11')).toBe(false);
    expect(isValidCPF('12345678900')).toBe(false);
    expect(isValidCPF('123')).toBe(false);
    expect(isValidCPF('')).toBe(false);
  });

  it('accepts valid CPFs', () => {
    // Standard valid CPF test cases
    expect(isValidCPF('52998224725')).toBe(true);
    expect(isValidCPF('529.982.247-25')).toBe(true);
  });

  it('formats CPF correctly', () => {
    expect(formatCPF('52998224725')).toBe('529.982.247-25');
  });
});

describe('CNPJ Validator', () => {
  it('rejects invalid checksums and repetitive patterns', () => {
    expect(isValidCNPJ('00.000.000/0000-00')).toBe(false);
    expect(isValidCNPJ('11.111.111/1111-11')).toBe(false);
    expect(isValidCNPJ('12.345.678/0001-99')).toBe(false);
    expect(isValidCNPJ('')).toBe(false);
  });

  it('accepts valid CNPJs', () => {
    expect(isValidCNPJ('00.000.000/0001-91')).toBe(true);
    expect(isValidCNPJ('00000000000191')).toBe(true);
  });

  it('formats CNPJ correctly', () => {
    expect(formatCNPJ('00000000000191')).toBe('00.000.000/0001-91');
  });
});

describe('SerproValidator', () => {
  it('rejects documents with invalid checksum before making API call', async () => {
    const fetcher = vi.fn();
    const validator = new SerproValidator({ apiKey: 'test-key', fetcher });

    const result = await validator.validateDocument('123.456.789-00');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('Invalid CPF checksum');
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('queries Serpro API for valid document', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({ nome: 'JOAO SILVA', situacao: { descricao: 'REGULAR' } })
    } as Response;
    const fetcher = vi.fn().mockResolvedValue(mockResponse);

    const validator = new SerproValidator({ apiKey: 'test-key', fetcher });
    const result = await validator.validateDocument('52998224725');

    expect(result.valid).toBe(true);
    expect(result.name).toBe('JOAO SILVA');
    expect(result.status).toBe('REGULAR');
    expect(fetcher).toHaveBeenCalled();
  });
});

describe('ReceitaWSValidator', () => {
  it('rejects CNPJ with invalid checksum without API call', async () => {
    const fetcher = vi.fn();
    const validator = new ReceitaWSValidator({ fetcher });

    const result = await validator.validateCNPJ('12.345.678/0001-99');
    expect(result.valid).toBe(false);
    expect(result.reason).toBe('Invalid CNPJ checksum');
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('queries ReceitaWS for valid CNPJ', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        status: 'OK',
        situacao: 'ATIVA',
        nome: 'EMPRESA TESTE LTDA',
        cnpj: '00.000.000/0001-91'
      })
    } as Response;
    const fetcher = vi.fn().mockResolvedValue(mockResponse);

    const validator = new ReceitaWSValidator({ fetcher });
    const result = await validator.validateCNPJ('00.000.000/0001-91');

    expect(result.valid).toBe(true);
    expect(result.nome).toBe('EMPRESA TESTE LTDA');
    expect(result.situacao).toBe('ATIVA');
    expect(fetcher).toHaveBeenCalled();
  });
});

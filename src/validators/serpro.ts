import { isValidCPF } from './cpf.js';
import { isValidCNPJ } from './cnpj.js';

export interface SerproValidationResult {
  valid: boolean;
  type?: 'CPF' | 'CNPJ';
  status?: 'REGULAR' | 'SUSPENSA' | 'CANCELADA' | 'BAIXADA' | 'NULA' | 'UNKNOWN';
  name?: string;
  reason?: string;
}

export interface SerproClientOptions {
  apiKey?: string;
  baseUrl?: string;
  fetcher?: (url: string, options?: RequestInit) => Promise<Response>;
}

export class SerproValidator {
  private apiKey?: string;
  private baseUrl: string;
  private fetcher: (url: string, options?: RequestInit) => Promise<Response>;

  constructor(options: SerproClientOptions = {}) {
    this.apiKey = options.apiKey || process.env.SERPRO_API_KEY;
    this.baseUrl = options.baseUrl || 'https://gateway.apivalidacao.serpro.gov.br';
    this.fetcher = options.fetcher || globalThis.fetch;
  }

  async validateDocument(document: string): Promise<SerproValidationResult> {
    const cleaned = document.replace(/\D/g, '');

    if (cleaned.length === 11) {
      if (!isValidCPF(cleaned)) {
        return { valid: false, type: 'CPF', reason: 'Invalid CPF checksum' };
      }
      return this.consultCPF(cleaned);
    } else if (cleaned.length === 14) {
      if (!isValidCNPJ(cleaned)) {
        return { valid: false, type: 'CNPJ', reason: 'Invalid CNPJ checksum' };
      }
      return this.consultCNPJ(cleaned);
    } else {
      return { valid: false, reason: 'Document must be 11 digits (CPF) or 14 digits (CNPJ)' };
    }
  }

  private async consultCPF(cpf: string): Promise<SerproValidationResult> {
    if (!this.apiKey) {
      // Mock / Offline mode when API key is not provided
      return {
        valid: true,
        type: 'CPF',
        status: 'REGULAR',
        name: 'MOCK SERPRO USER'
      };
    }

    try {
      const response = await this.fetcher(`${this.baseUrl}/consulta-cpf/v1/cpf/${cpf}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        return { valid: false, type: 'CPF', reason: `Serpro API error: ${response.statusText}` };
      }

      const data = await response.json() as { situacao?: { codigo?: string; descricao?: string }; nome?: string };
      const statusDesc = data.situacao?.descricao?.toUpperCase() || 'REGULAR';
      const isRegular = statusDesc === 'REGULAR';

      return {
        valid: isRegular,
        type: 'CPF',
        status: (statusDesc as SerproValidationResult['status']) || 'UNKNOWN',
        name: data.nome
      };
    } catch (error) {
      return { valid: false, type: 'CPF', reason: `Failed to query Serpro API: ${(error as Error).message}` };
    }
  }

  private async consultCNPJ(cnpj: string): Promise<SerproValidationResult> {
    if (!this.apiKey) {
      // Mock / Offline mode when API key is not provided
      return {
        valid: true,
        type: 'CNPJ',
        status: 'REGULAR',
        name: 'MOCK SERPRO COMPANY LTDA'
      };
    }

    try {
      const response = await this.fetcher(`${this.baseUrl}/consulta-cnpj/v1/cnpj/${cnpj}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        return { valid: false, type: 'CNPJ', reason: `Serpro API error: ${response.statusText}` };
      }

      const data = await response.json() as { situacaoCadastral?: { descricao?: string }; razasocial?: string; nomeFantasia?: string };
      const statusDesc = data.situacaoCadastral?.descricao?.toUpperCase() || 'REGULAR';
      const isRegular = statusDesc === 'REGULAR' || statusDesc === 'ATIVA';

      return {
        valid: isRegular,
        type: 'CNPJ',
        status: (statusDesc as SerproValidationResult['status']) || 'UNKNOWN',
        name: data.razasocial || data.nomeFantasia
      };
    } catch (error) {
      return { valid: false, type: 'CNPJ', reason: `Failed to query Serpro API: ${(error as Error).message}` };
    }
  }
}

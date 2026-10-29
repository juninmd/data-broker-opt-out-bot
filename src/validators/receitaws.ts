import { isValidCNPJ } from './cnpj.js';

export interface ReceitaWSResult {
  valid: boolean;
  status?: string;
  situacao?: string;
  nome?: string;
  fantasia?: string;
  cnpj?: string;
  reason?: string;
}

export interface ReceitaWSOptions {
  baseUrl?: string;
  fetcher?: (url: string, options?: RequestInit) => Promise<Response>;
}

export class ReceitaWSValidator {
  private baseUrl: string;
  private fetcher: (url: string, options?: RequestInit) => Promise<Response>;

  constructor(options: ReceitaWSOptions = {}) {
    this.baseUrl = options.baseUrl || 'https://receitaws.com.br/v1/cnpj';
    this.fetcher = options.fetcher || globalThis.fetch;
  }

  async validateCNPJ(cnpj: string): Promise<ReceitaWSResult> {
    const cleaned = cnpj.replace(/\D/g, '');

    if (!isValidCNPJ(cleaned)) {
      return {
        valid: false,
        reason: 'Invalid CNPJ checksum'
      };
    }

    try {
      const response = await this.fetcher(`${this.baseUrl}/${cleaned}`);

      if (!response.ok) {
        return {
          valid: false,
          reason: `ReceitaWS API returned status ${response.status}`
        };
      }

      const data = await response.json() as {
        status?: string;
        situacao?: string;
        nome?: string;
        fantasia?: string;
        cnpj?: string;
        message?: string;
      };

      if (data.status === 'ERROR') {
        return {
          valid: false,
          reason: data.message || 'ReceitaWS query failed'
        };
      }

      const isAtiva = data.situacao?.toUpperCase() === 'ATIVA';

      return {
        valid: isAtiva,
        status: data.status,
        situacao: data.situacao,
        nome: data.nome,
        fantasia: data.fantasia,
        cnpj: data.cnpj
      };
    } catch (error) {
      return {
        valid: false,
        reason: `Failed to query ReceitaWS: ${(error as Error).message}`
      };
    }
  }
}

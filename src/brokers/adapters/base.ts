import { BrokerAdapter, BrokerInfo, OptOutRequest, OptOutResponse, ParsedFixtureResult } from '../types.js';
import { isValidCPF } from '../../validators/cpf.js';
import { isValidCNPJ } from '../../validators/cnpj.js';

export abstract class BaseBrokerAdapter implements BrokerAdapter {
  abstract readonly info: BrokerInfo;

  abstract parseFixture(fixtureContent: string): ParsedFixtureResult;

  async processOptOut(request: OptOutRequest, fixtureContent?: string): Promise<OptOutResponse> {
    const cleanedDoc = request.document ? request.document.replace(/\D/g, '') : '';

    // Checksum validation
    const valid = cleanedDoc.length === 11
      ? isValidCPF(cleanedDoc)
      : (cleanedDoc.length === 14 ? isValidCNPJ(cleanedDoc) : false);

    if (!valid) {
      return {
        success: false,
        brokerId: this.info.id,
        message: 'Invalid CPF or CNPJ checksum provided',
        timestamp: new Date().toISOString()
      };
    }

    if (fixtureContent) {
      const parsed = this.parseFixture(fixtureContent);
      return {
        success: parsed.success,
        brokerId: this.info.id,
        requestId: parsed.requestId,
        message: parsed.message,
        timestamp: new Date().toISOString()
      };
    }

    // Default simulation for active adapter when no fixture provided
    return {
      success: true,
      brokerId: this.info.id,
      requestId: `${this.info.id.toUpperCase()}-SIM-${Date.now()}`,
      message: `Opt-out request submitted successfully to ${this.info.name}`,
      timestamp: new Date().toISOString()
    };
  }
}

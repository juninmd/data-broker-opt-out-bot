import { BaseBrokerAdapter } from './base.js';
import { BrokerInfo, ParsedFixtureResult } from '../types.js';

export class ListaTelefonicaAdapter extends BaseBrokerAdapter {
  readonly info: BrokerInfo = {
    id: 'listatelefonica',
    name: 'Lista Telefônica',
    country: 'BR',
    website: 'https://listatelefonica.com.br',
    optOutUrl: 'https://listatelefonica.com.br/optout',
    requiresDocument: true,
    status: 'active'
  };

  parseFixture(fixtureContent: string): ParsedFixtureResult {
    if (fixtureContent.includes('SUCCESS') || fixtureContent.includes('LT-OPT-')) {
      const match = fixtureContent.match(/Protocolo:\s*([A-Z0-9-]+)/i);
      return {
        success: true,
        status: 'SUCCESS',
        message: 'Opt-out submitted successfully to Lista Telefônica',
        requestId: match ? match[1] : 'LT-OPT-UNKNOWN'
      };
    }

    if (fixtureContent.includes('result-card')) {
      return {
        success: true,
        status: 'PROFILE_FOUND',
        message: 'Profile identified on Lista Telefônica'
      };
    }

    return {
      success: false,
      status: 'ERROR',
      message: 'Failed to process opt-out for Lista Telefônica'
    };
  }
}

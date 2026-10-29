import { BaseBrokerAdapter } from './base.js';
import { BrokerInfo, ParsedFixtureResult } from '../types.js';

export class ApontadorAdapter extends BaseBrokerAdapter {
  readonly info: BrokerInfo = {
    id: 'apontador',
    name: 'Apontador',
    country: 'BR',
    website: 'https://apontador.com.br',
    optOutUrl: 'https://apontador.com.br/privacidade/optout',
    requiresDocument: true,
    status: 'active'
  };

  parseFixture(fixtureContent: string): ParsedFixtureResult {
    if (fixtureContent.includes('CONFIRMED') || fixtureContent.includes('APT-')) {
      const match = fixtureContent.match(/Protocolo:\s*([A-Z0-9-]+)/i);
      return {
        success: true,
        status: 'CONFIRMED',
        message: 'Opt-out submitted successfully to Apontador',
        requestId: match ? match[1] : 'APT-UNKNOWN'
      };
    }

    if (fixtureContent.includes('profile-box')) {
      return {
        success: true,
        status: 'PROFILE_FOUND',
        message: 'Profile identified on Apontador'
      };
    }

    return {
      success: false,
      status: 'FAILED',
      message: 'Failed to process opt-out for Apontador'
    };
  }
}

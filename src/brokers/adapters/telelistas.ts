import { BaseBrokerAdapter } from './base.js';
import { BrokerInfo, ParsedFixtureResult } from '../types.js';

export class TeleListasAdapter extends BaseBrokerAdapter {
  readonly info: BrokerInfo = {
    id: 'telelistas',
    name: 'TeleListas',
    country: 'BR',
    website: 'https://telelistas.net',
    optOutUrl: 'https://telelistas.net/optout',
    requiresDocument: true,
    status: 'active'
  };

  parseFixture(fixtureContent: string): ParsedFixtureResult {
    if (fixtureContent.includes('OPTOUT_COMPLETED') || fixtureContent.includes('TL-')) {
      const match = fixtureContent.match(/num_protocolo["']>([A-Z0-9-]+)</i);
      return {
        success: true,
        status: 'OPTOUT_COMPLETED',
        message: 'Opt-out completed successfully on TeleListas',
        requestId: match ? match[1] : 'TL-UNKNOWN'
      };
    }

    if (fixtureContent.includes('site_resultado')) {
      return {
        success: true,
        status: 'PROFILE_FOUND',
        message: 'Profile found on TeleListas'
      };
    }

    return {
      success: false,
      status: 'OPTOUT_FAILED',
      message: 'TeleListas opt-out request failed'
    };
  }
}

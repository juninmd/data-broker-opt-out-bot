import { BaseBrokerAdapter } from './base.js';
import { BrokerInfo, ParsedFixtureResult } from '../types.js';

export class Broker118Adapter extends BaseBrokerAdapter {
  readonly info: BrokerInfo = {
    id: '118',
    name: '118 Telelista',
    country: 'BR',
    website: 'https://118.com.br',
    optOutUrl: 'https://118.com.br/lgpd/optout',
    requiresDocument: true,
    status: 'active'
  };

  parseFixture(fixtureContent: string): ParsedFixtureResult {
    if (fixtureContent.includes('SUCCESSFUL_REMOVAL') || fixtureContent.includes('REF118-')) {
      const match = fixtureContent.match(/REF118-[0-9]+/i);
      return {
        success: true,
        status: 'SUCCESSFUL_REMOVAL',
        message: 'Opt-out completed successfully on 118',
        requestId: match ? match[0] : 'REF118-UNKNOWN'
      };
    }

    if (fixtureContent.includes('118-listing')) {
      return {
        success: true,
        status: 'PROFILE_FOUND',
        message: 'Listing found on 118'
      };
    }

    return {
      success: false,
      status: 'INVALID_REQUEST',
      message: '118 opt-out request failed'
    };
  }
}

import { BaseBrokerAdapter } from './base.js';
import { BrokerInfo, ParsedFixtureResult } from '../types.js';

export class GuiaMaisAdapter extends BaseBrokerAdapter {
  readonly info: BrokerInfo = {
    id: 'guiamais',
    name: 'GuiaMais',
    country: 'BR',
    website: 'https://guiamais.com.br',
    optOutUrl: 'https://guiamais.com.br/privacidade/remover',
    requiresDocument: true,
    status: 'active'
  };

  parseFixture(fixtureContent: string): ParsedFixtureResult {
    if (fixtureContent.includes('200_OK') || fixtureContent.includes('GM-REQ-')) {
      const match = fixtureContent.match(/GM-REQ-[0-9]+/i);
      return {
        success: true,
        status: '200_OK',
        message: 'Opt-out processed successfully on GuiaMais',
        requestId: match ? match[0] : 'GM-REQ-UNKNOWN'
      };
    }

    if (fixtureContent.includes('listing-details')) {
      return {
        success: true,
        status: 'PROFILE_FOUND',
        message: 'Listing found on GuiaMais'
      };
    }

    return {
      success: false,
      status: '400_BAD_REQUEST',
      message: 'GuiaMais opt-out request failed'
    };
  }
}

export interface OptOutRequest {
  fullName: string;
  document: string; // CPF or CNPJ
  email: string;
  phone?: string;
  reason?: string;
}

export interface OptOutResponse {
  success: boolean;
  brokerId: string;
  requestId?: string;
  message: string;
  timestamp: string;
}

export interface BrokerInfo {
  id: string;
  name: string;
  country: 'BR' | 'US';
  website: string;
  optOutUrl: string;
  requiresDocument: boolean;
  status: 'active' | 'maintenance' | 'deprecated';
}

export interface ParsedFixtureResult {
  success: boolean;
  status: string;
  message: string;
  requestId?: string;
}

export interface BrokerAdapter {
  readonly info: BrokerInfo;
  processOptOut(request: OptOutRequest, fixtureContent?: string): Promise<OptOutResponse>;
  parseFixture(fixtureContent: string): ParsedFixtureResult;
}

import { BrokerAdapter } from './types.js';
import { ListaTelefonicaAdapter } from './adapters/listatelefonica.js';
import { ApontadorAdapter } from './adapters/apontador.js';
import { GuiaMaisAdapter } from './adapters/guiamais.js';
import { TeleListasAdapter } from './adapters/telelistas.js';
import { Broker118Adapter } from './adapters/broker118.js';

export class BrokerRegistry {
  private adapters: Map<string, BrokerAdapter> = new Map();

  constructor() {
    this.registerDefaults();
  }

  private registerDefaults() {
    this.register(new ListaTelefonicaAdapter());
    this.register(new ApontadorAdapter());
    this.register(new GuiaMaisAdapter());
    this.register(new TeleListasAdapter());
    this.register(new Broker118Adapter());
  }

  register(adapter: BrokerAdapter): void {
    this.adapters.set(adapter.info.id.toLowerCase(), adapter);
  }

  getAdapter(id: string): BrokerAdapter | undefined {
    return this.adapters.get(id.toLowerCase());
  }

  getAllAdapters(): BrokerAdapter[] {
    return Array.from(this.adapters.values());
  }

  getBrazilianPack(): BrokerAdapter[] {
    return this.getAllAdapters().filter(adapter => adapter.info.country === 'BR');
  }
}

export const defaultRegistry = new BrokerRegistry();

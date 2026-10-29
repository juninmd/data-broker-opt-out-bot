import { createDatabase } from '../src/db/database';
import { BrokerHealthService } from '../src/services/broker-health.service';
import { BotCommandHandler } from '../src/bot/commands';

describe('BotCommandHandler', () => {
  let healthService: BrokerHealthService;
  let commandHandler: BotCommandHandler;

  beforeEach(() => {
    const db = createDatabase(':memory:');
    healthService = new BrokerHealthService(db);
    commandHandler = new BotCommandHandler(healthService);

    healthService.registerBroker('clear-sale', 'ClearSale');
    healthService.registerBroker('serasa', 'Serasa Experian');
  });

  test('/brokers command lists registered brokers with statuses', () => {
    let output = commandHandler.handleBrokersCommand();
    expect(output).toContain('ClearSale (clear-sale) - Status: ACTIVE');
    expect(output).toContain('Serasa Experian (serasa) - Status: ACTIVE');

    // Simulate 2 failures -> degraded
    healthService.recordExecution('clear-sale', false);
    healthService.recordExecution('clear-sale', false);

    output = commandHandler.handleBrokersCommand();
    expect(output).toContain('⚠️ ClearSale (clear-sale) - Status: DEGRADED');
  });

  test('/health command shows detailed metrics per broker', () => {
    healthService.recordExecution('serasa', true);
    healthService.recordExecution('serasa', true);
    healthService.recordExecution('serasa', false);

    const healthOutput = commandHandler.handleHealthCommand();
    expect(healthOutput).toContain('*Broker Health & Metrics:*');
    expect(healthOutput).toContain('Serasa Experian');
    expect(healthOutput).toContain('Success Rate: 66.7% (2/3)');
    expect(healthOutput).toContain('Consecutive Failures: 1');
  });

  test('/enable command re-enables disabled adapter', () => {
    // Fail clear-sale 5 times to auto-disable
    for (let i = 0; i < 5; i++) {
      healthService.recordExecution('clear-sale', false);
    }
    expect(healthService.getBroker('clear-sale')?.status).toBe('disabled');

    const enableResult = commandHandler.handleEnableCommand('clear-sale');
    expect(enableResult).toContain("Adapter for broker 'ClearSale' (clear-sale) has been successfully re-enabled.");
    expect(healthService.getBroker('clear-sale')?.status).toBe('active');
  });

  test('/enable command handles invalid broker ID', () => {
    const result = commandHandler.handleEnableCommand('non-existent');
    expect(result).toContain("Broker 'non-existent' not found.");
  });
});

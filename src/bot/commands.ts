import { BrokerHealthService, BrokerRecord } from '../services/broker-health.service';

export class BotCommandHandler {
  private healthService: BrokerHealthService;

  constructor(healthService: BrokerHealthService) {
    this.healthService = healthService;
  }

  /**
   * Handles /brokers command
   * Returns list of brokers and their current status ('active', 'degraded', 'disabled')
   */
  public handleBrokersCommand(): string {
    const brokers = this.healthService.getAllBrokers();

    if (brokers.length === 0) {
      return 'No brokers registered.';
    }

    const lines = brokers.map((b) => {
      const statusSymbol =
        b.status === 'active' ? '✅' : b.status === 'degraded' ? '⚠️' : '❌';
      return `${statusSymbol} ${b.name} (${b.id}) - Status: ${b.status.toUpperCase()}`;
    });

    return `*Broker List:*\n${lines.join('\n')}`;
  }

  /**
   * Handles /health command (Admin command)
   * Shows detailed health metrics per broker
   */
  public handleHealthCommand(): string {
    const brokers = this.healthService.getAllBrokers();

    if (brokers.length === 0) {
      return 'No broker metrics available.';
    }

    const header = '*Broker Health & Metrics:*';
    const report = brokers.map((b) => {
      const successRate =
        b.total_requests > 0
          ? ((b.successful_requests / b.total_requests) * 100).toFixed(1)
          : '100.0';

      return (
        `• *${b.name}* [ID: \`${b.id}\`]\n` +
        `  Status: ${b.status.toUpperCase()}\n` +
        `  Success Rate: ${successRate}% (${b.successful_requests}/${b.total_requests})\n` +
        `  Consecutive Failures: ${b.consecutive_failures}\n` +
        `  Failed Requests: ${b.failed_requests}` +
        (b.disabled_at ? `\n  Disabled At: ${b.disabled_at}` : '')
      );
    });

    return `${header}\n\n${report.join('\n\n')}`;
  }

  /**
   * Handles /enable <broker_id> command (Admin command)
   * Manually re-enables a disabled adapter
   */
  public handleEnableCommand(brokerId: string): string {
    if (!brokerId || !brokerId.trim()) {
      return 'Usage: /enable <broker_id>';
    }

    try {
      const updated = this.healthService.reEnableBroker(brokerId.trim());
      return `✅ Adapter for broker '${updated.name}' (${updated.id}) has been successfully re-enabled.`;
    } catch (err: any) {
      return `❌ Error: ${err.message}`;
    }
  }
}

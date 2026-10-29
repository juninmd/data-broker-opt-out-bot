import { createDatabase } from '../src/db/database';
import { BrokerHealthService } from '../src/services/broker-health.service';

describe('BrokerHealthService', () => {
  let healthService: BrokerHealthService;

  beforeEach(() => {
    const db = createDatabase(':memory:');
    healthService = new BrokerHealthService(db);
  });

  test('registers and retrieves a broker', () => {
    const broker = healthService.registerBroker('clear-sale', 'ClearSale');
    expect(broker).toBeDefined();
    expect(broker.id).toBe('clear-sale');
    expect(broker.name).toBe('ClearSale');
    expect(broker.status).toBe('active');
    expect(broker.consecutive_failures).toBe(0);
  });

  test('records successful executions', () => {
    healthService.registerBroker('serasa', 'Serasa Experian');
    const updated = healthService.recordExecution('serasa', true);
    expect(updated.status).toBe('active');
    expect(updated.total_requests).toBe(1);
    expect(updated.successful_requests).toBe(1);
    expect(updated.failed_requests).toBe(0);
    expect(updated.consecutive_failures).toBe(0);
  });

  test('marks broker as degraded on <5 failures', () => {
    healthService.registerBroker('boavista', 'Boa Vista');
    let updated = healthService.recordExecution('boavista', false);
    expect(updated.status).toBe('degraded');
    expect(updated.consecutive_failures).toBe(1);

    updated = healthService.recordExecution('boavista', false);
    expect(updated.status).toBe('degraded');
    expect(updated.consecutive_failures).toBe(2);
  });

  test('auto-disables broker on 5 consecutive failures and sends notification', () => {
    healthService.registerBroker('spc', 'SPC Brasil');
    const listener = jest.fn();
    healthService.registerNotificationListener(listener);

    for (let i = 1; i <= 4; i++) {
      const b = healthService.recordExecution('spc', false);
      expect(b.status).toBe('degraded');
      expect(b.consecutive_failures).toBe(i);
    }

    expect(listener).not.toHaveBeenCalled();

    const fifth = healthService.recordExecution('spc', false);
    expect(fifth.status).toBe('disabled');
    expect(fifth.consecutive_failures).toBe(5);
    expect(fifth.disabled_at).not.toBeNull();

    expect(listener).toHaveBeenCalledTimes(1);
    expect(listener).toHaveBeenCalledWith(
      expect.objectContaining({
        brokerId: 'spc',
        message: expect.stringContaining("auto-disabled after 5 consecutive failures"),
      })
    );

    const notifications = healthService.getAdminNotifications();
    expect(notifications.length).toBe(1);
    expect(notifications[0].broker_id).toBe('spc');
  });

  test('resets consecutive failures counter on success', () => {
    healthService.registerBroker('transunion', 'TransUnion');
    healthService.recordExecution('transunion', false);
    healthService.recordExecution('transunion', false);
    expect(healthService.getBroker('transunion')?.consecutive_failures).toBe(2);

    const recovered = healthService.recordExecution('transunion', true);
    expect(recovered.consecutive_failures).toBe(0);
    expect(recovered.status).toBe('active');
  });

  test('allows manual re-enabling of disabled broker', () => {
    healthService.registerBroker('equifax', 'Equifax');
    for (let i = 0; i < 5; i++) {
      healthService.recordExecution('equifax', false);
    }
    expect(healthService.getBroker('equifax')?.status).toBe('disabled');

    const reEnabled = healthService.reEnableBroker('equifax');
    expect(reEnabled.status).toBe('active');
    expect(reEnabled.consecutive_failures).toBe(0);
    expect(reEnabled.disabled_at).toBeNull();
  });
});

import Database from 'better-sqlite3';

export type BrokerStatus = 'active' | 'degraded' | 'disabled';

export interface BrokerRecord {
  id: string;
  name: string;
  status: BrokerStatus;
  consecutive_failures: number;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  disabled_at: string | null;
  updated_at: string;
}

export interface AdminNotification {
  id: number;
  broker_id: string;
  message: string;
  created_at: string;
}

export type AdminNotificationListener = (notification: { brokerId: string; message: string; timestamp: string }) => void;

export class BrokerHealthService {
  private db: Database.Database;
  private notificationListeners: AdminNotificationListener[] = [];

  constructor(db: Database.Database) {
    this.db = db;
  }

  public registerNotificationListener(listener: AdminNotificationListener): void {
    this.notificationListeners.push(listener);
  }

  public registerBroker(id: string, name: string): BrokerRecord {
    const now = new Date().toISOString();
    const existing = this.getBroker(id);
    if (existing) {
      return existing;
    }

    const stmt = this.db.prepare(`
      INSERT INTO brokers (id, name, status, consecutive_failures, total_requests, successful_requests, failed_requests, disabled_at, updated_at)
      VALUES (?, ?, 'active', 0, 0, 0, 0, NULL, ?)
    `);
    stmt.run(id, name, now);
    return this.getBroker(id)!;
  }

  public getBroker(id: string): BrokerRecord | null {
    const stmt = this.db.prepare('SELECT * FROM brokers WHERE id = ?');
    const row = stmt.get(id) as BrokerRecord | undefined;
    return row || null;
  }

  public getAllBrokers(): BrokerRecord[] {
    const stmt = this.db.prepare('SELECT * FROM brokers ORDER BY id ASC');
    return stmt.all() as BrokerRecord[];
  }

  public recordExecution(brokerId: string, success: boolean): BrokerRecord {
    let broker = this.getBroker(brokerId);
    if (!broker) {
      broker = this.registerBroker(brokerId, brokerId);
    }

    // If disabled, skip execution or keep recorded metrics
    if (broker.status === 'disabled') {
      return broker;
    }

    const now = new Date().toISOString();
    let newConsecutiveFailures = success ? 0 : broker.consecutive_failures + 1;
    let newStatus: BrokerStatus = broker.status;
    let disabledAt: string | null = broker.disabled_at;
    let triggeredDisable = false;

    if (!success) {
      if (newConsecutiveFailures >= 5) {
        newStatus = 'disabled';
        disabledAt = now;
        triggeredDisable = true;
      } else {
        newStatus = 'degraded';
      }
    } else {
      newStatus = 'active';
    }

    const totalRequests = broker.total_requests + 1;
    const successfulRequests = broker.successful_requests + (success ? 1 : 0);
    const failedRequests = broker.failed_requests + (success ? 0 : 1);

    const updateStmt = this.db.prepare(`
      UPDATE brokers
      SET status = ?,
          consecutive_failures = ?,
          total_requests = ?,
          successful_requests = ?,
          failed_requests = ?,
          disabled_at = ?,
          updated_at = ?
      WHERE id = ?
    `);

    updateStmt.run(
      newStatus,
      newConsecutiveFailures,
      totalRequests,
      successfulRequests,
      failedRequests,
      disabledAt,
      now,
      brokerId
    );

    if (triggeredDisable) {
      this.notifyAdmin(brokerId, `Broker adapter '${broker.name}' (${brokerId}) auto-disabled after 5 consecutive failures.`, now);
    }

    return this.getBroker(brokerId)!;
  }

  public reEnableBroker(brokerId: string): BrokerRecord {
    const broker = this.getBroker(brokerId);
    if (!broker) {
      throw new Error(`Broker '${brokerId}' not found.`);
    }

    const now = new Date().toISOString();
    const stmt = this.db.prepare(`
      UPDATE brokers
      SET status = 'active',
          consecutive_failures = 0,
          disabled_at = NULL,
          updated_at = ?
      WHERE id = ?
    `);
    stmt.run(now, brokerId);

    return this.getBroker(brokerId)!;
  }

  public getAdminNotifications(): AdminNotification[] {
    const stmt = this.db.prepare('SELECT * FROM admin_notifications ORDER BY id DESC');
    return stmt.all() as AdminNotification[];
  }

  private notifyAdmin(brokerId: string, message: string, timestamp: string): void {
    const stmt = this.db.prepare(`
      INSERT INTO admin_notifications (broker_id, message, created_at)
      VALUES (?, ?, ?)
    `);
    stmt.run(brokerId, message, timestamp);

    for (const listener of this.notificationListeners) {
      try {
        listener({ brokerId, message, timestamp });
      } catch (err) {
        // Log or handle error without crashing
      }
    }
  }
}

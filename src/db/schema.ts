import Database from 'better-sqlite3';

export const CREATE_BROKERS_TABLE = `
CREATE TABLE IF NOT EXISTS brokers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  consecutive_failures INTEGER DEFAULT 0,
  total_requests INTEGER DEFAULT 0,
  successful_requests INTEGER DEFAULT 0,
  failed_requests INTEGER DEFAULT 0,
  disabled_at TEXT,
  updated_at TEXT NOT NULL
);
`;

export const CREATE_ADMIN_NOTIFICATIONS_TABLE = `
CREATE TABLE IF NOT EXISTS admin_notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  broker_id TEXT NOT NULL,
  message TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (broker_id) REFERENCES brokers (id)
);
`;

export function initializeDatabase(db: Database.Database): void {
  db.exec(CREATE_BROKERS_TABLE);
  db.exec(CREATE_ADMIN_NOTIFICATIONS_TABLE);
}

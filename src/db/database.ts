import Database from 'better-sqlite3';
import { initializeDatabase } from './schema';

export function createDatabase(dbPath: string = ':memory:'): Database.Database {
  const db = new Database(dbPath);
  db.pragma('foreign_keys = ON');
  initializeDatabase(db);
  return db;
}

import { db } from "../db/db";
import { Vendor } from "../types";

const findAll = (): Vendor[] => {
  return db.prepare("SELECT * FROM vendors").all() as Vendor[];
};

const findById = (id: number): Vendor | undefined => {
  return db.prepare("SELECT * FROM vendors WHERE id = ?").get(id) as
    | Vendor
    | undefined;
};

const findByEmail = (email: string): Vendor | undefined => {
  return db.prepare("SELECT * FROM vendors WHERE email = ?").get(email) as
    | Vendor
    | undefined;
};

const create = (vendor: Vendor): number => {
  const insertStatement = db.prepare(
    "INSERT INTO vendors (name, email, phone_number) VALUES (?, ?, ?)",
  );
  const executionResult = insertStatement.run(
    vendor.name,
    vendor.email,
    vendor.phone_number,
  );
  return executionResult.lastInsertRowid as number;
};

const update = (id: number, vendor: Partial<Vendor>): void => {
  const keys = Object.keys(vendor);
  if (keys.length === 0) return;

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => (vendor as any)[key]);

  const updateStatement = db.prepare(
    `UPDATE vendors SET ${setClause} WHERE id = ?`,
  );
  updateStatement.run(...values, id);
};

const deleteById = (id: number): void => {
  db.prepare("DELETE FROM vendors WHERE id = ?").run(id);
};

export default {
  findAll,
  findById,
  findByEmail,
  create,
  update,
  deleteById,
};

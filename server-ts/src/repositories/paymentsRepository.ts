import { db } from "../db/db";
import { Payment } from "../types";

const findAll = (): Payment[] => {
  return db.prepare("SELECT * FROM payments").all() as Payment[];
};

const findById = (id: number): Payment | undefined => {
  return db.prepare("SELECT * FROM payments WHERE id = ?").get(id) as
    | Payment
    | undefined;
};

const create = (payment: Payment): number => {
  const insertStatement = db.prepare("INSERT INTO payments (name) VALUES (?)");
  const executionResult = insertStatement.run(payment.name);
  return executionResult.lastInsertRowid as number;
};

const update = (id: number, payment: Partial<Payment>): void => {
  const keys = Object.keys(payment);
  if (keys.length === 0) return;

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => (payment as any)[key]);

  const updateStatement = db.prepare(
    `UPDATE payments SET ${setClause} WHERE id = ?`,
  );
  updateStatement.run(...values, id);
};

const deleteById = (id: number): void => {
  db.prepare("DELETE FROM payments WHERE id = ?").run(id);
};

export default {
  findAll,
  findById,
  create,
  update,
  deleteById,
};

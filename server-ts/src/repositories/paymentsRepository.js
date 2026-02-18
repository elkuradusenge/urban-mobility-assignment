import { db } from "../db/db.js";

const findAll = () => {
  return db.prepare("SELECT * FROM payments").all();
};

const findById = (id) => {
  return db.prepare("SELECT * FROM payments WHERE id = ?").get(id);
};

const findByName = (name) => {
  return db.prepare("SELECT * FROM payments WHERE name = ?").get(name);
};

const create = (payment) => {
  const insertStatement = db.prepare("INSERT INTO payments (name) VALUES (?)");
  const executionResult = insertStatement.run(payment.name);
  return executionResult.lastInsertRowid;
};

const update = (id, payment) => {
  const keys = Object.keys(payment);
  if (keys.length === 0) return;

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => payment[key]);

  const updateStatement = db.prepare(
    `UPDATE payments SET ${setClause} WHERE id = ?`,
  );
  updateStatement.run(...values, id);
};

const deleteById = (id) => {
  db.prepare("DELETE FROM payments WHERE id = ?").run(id);
};

export default {
  findAll,
  findById,
  findByName,
  create,
  update,
  deleteById,
};

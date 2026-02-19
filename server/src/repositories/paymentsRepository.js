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
  const insertStatement = db.prepare("INSERT INTO payments (name) VALUES (?) RETURNING *");
  return insertStatement.get(payment.name);
};

const update = (id, payment) => {
  const keys = Object.keys(payment);
  if (keys.length === 0) return db.prepare("SELECT * FROM payments WHERE id = ?").get(id);

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => payment[key]);

  const updateStatement = db.prepare(
    `UPDATE payments SET ${setClause} WHERE id = ? RETURNING *`,
  );
  return updateStatement.get(...values, id);
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

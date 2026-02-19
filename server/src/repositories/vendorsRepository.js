import { db } from "../db/db.js";

const findAll = () => {
  return db.prepare("SELECT * FROM vendors").all();
};

const findById = (id) => {
  return db.prepare("SELECT * FROM vendors WHERE id = ?").get(id);
};

const findByEmail = (email) => {
  return db.prepare("SELECT * FROM vendors WHERE email = ?").get(email);
};

const create = (vendor) => {
  const insertStatement = db.prepare(
    "INSERT INTO vendors (name, email, phone_number) VALUES (?, ?, ?) RETURNING *",
  );
  return insertStatement.get(
    vendor.name,
    vendor.email,
    vendor.phone_number,
  );
};

const update = (id, vendor) => {
  const keys = Object.keys(vendor);
  if (keys.length === 0) return db.prepare("SELECT * FROM vendors WHERE id = ?").get(id);

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => vendor[key]);

  const updateStatement = db.prepare(
    `UPDATE vendors SET ${setClause} WHERE id = ? RETURNING *`,
  );
  return updateStatement.get(...values, id);
};

const deleteById = (id) => {
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

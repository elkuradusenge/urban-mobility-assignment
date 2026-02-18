import { db } from "../db/db.js";

const findAll = () => {
  return db.prepare("SELECT * FROM locations").all();
};

const findById = (id) => {
  return db.prepare("SELECT * FROM locations WHERE location_id = ?").get(id);
};

const create = (location) => {
  const insertStatement = db.prepare(
    "INSERT INTO locations (borough, zone, service_zone) VALUES (?, ?, ?)",
  );
  const executionResult = insertStatement.run(
    location.borough,
    location.zone,
    location.service_zone,
  );
  return executionResult.lastInsertRowid;
};

const update = (id, location) => {
  const keys = Object.keys(location);
  if (keys.length === 0) return;

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => location[key]);

  const updateStatement = db.prepare(
    `UPDATE locations SET ${setClause} WHERE location_id = ?`,
  );
  updateStatement.run(...values, id);
};

const deleteById = (id) => {
  db.prepare("DELETE FROM locations WHERE location_id = ?").run(id);
};

export default {
  findAll,
  findById,
  create,
  update,
  deleteById,
};

import { db } from "../db/db";
import { Location } from "../types";

const findAll = (): Location[] => {
  return db.prepare("SELECT * FROM locations").all() as Location[];
};

const findById = (id: number): Location | undefined => {
  return db.prepare("SELECT * FROM locations WHERE location_id = ?").get(id) as
    | Location
    | undefined;
};

const create = (location: Location): number => {
  const insertStatement = db.prepare(
    "INSERT INTO locations (borough, zone, service_zone) VALUES (?, ?, ?)",
  );
  const executionResult = insertStatement.run(
    location.borough,
    location.zone,
    location.service_zone,
  );
  return executionResult.lastInsertRowid as number;
};

const update = (id: number, location: Partial<Location>): void => {
  const keys = Object.keys(location);
  if (keys.length === 0) return;

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => (location as any)[key]);

  const updateStatement = db.prepare(
    `UPDATE locations SET ${setClause} WHERE location_id = ?`,
  );
  updateStatement.run(...values, id);
};

const deleteById = (id: number): void => {
  db.prepare("DELETE FROM locations WHERE location_id = ?").run(id);
};

export default {
  findAll,
  findById,
  create,
  update,
  deleteById,
};

import { db } from "../db/db";
import { Trip } from "../types";

const findAll = (): Trip[] => {
  return db.prepare("SELECT * FROM trips").all() as Trip[];
};

const findById = (id: number): Trip | undefined => {
  return db.prepare("SELECT * FROM trips WHERE id = ?").get(id) as
    | Trip
    | undefined;
};

const create = (trip: Trip): number => {
  const insertStatement = db.prepare(
    `INSERT INTO trips (
        vendor_id, 
        pickup_datetime, 
        dropoff_datetime, 
        passenger_count, 
        trip_distance, 
        mta_tax, 
        pickup_location_id, 
        dropoff_location_id, 
        tip_amount, 
        fare_amount, 
        total_amount
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  );
  const executionResult = insertStatement.run(
    trip.vendor_id,
    trip.pickup_datetime,
    trip.dropoff_datetime,
    trip.passenger_count,
    trip.trip_distance,
    trip.mta_tax,
    trip.pickup_location_id,
    trip.dropoff_location_id,
    trip.tip_amount,
    trip.fare_amount,
    trip.total_amount,
  );
  return executionResult.lastInsertRowid as number;
};

const update = (id: number, trip: Partial<Trip>): void => {
  const keys = Object.keys(trip);
  if (keys.length === 0) return;

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => (trip as any)[key]);

  const updateStatement = db.prepare(
    `UPDATE trips SET ${setClause} WHERE id = ?`,
  );
  updateStatement.run(...values, id);
};

const deleteById = (id: number): void => {
  db.prepare("DELETE FROM trips WHERE id = ?").run(id);
};

export default {
  findAll,
  findById,
  create,
  update,
  deleteById,
};

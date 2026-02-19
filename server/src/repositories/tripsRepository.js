import { db } from "../db/db.js";

const findAll = () => {
  return db.prepare("SELECT * FROM trips").all();
};

const findById = (id) => {
  return db.prepare("SELECT * FROM trips WHERE id = ?").get(id);
};

const create = (trip) => {
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
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING *`,
  );
  return insertStatement.get(
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
};

const update = (id, trip) => {
  const keys = Object.keys(trip);
  if (keys.length === 0) return db.prepare("SELECT * FROM trips WHERE id = ?").get(id);

  const setClause = keys.map((key) => `${key} = ?`).join(", ");
  const values = keys.map((key) => trip[key]);

  const updateStatement = db.prepare(
    `UPDATE trips SET ${setClause} WHERE id = ? RETURNING *`,
  );
  return updateStatement.get(...values, id);
};

const deleteById = (id) => {
  db.prepare("DELETE FROM trips WHERE id = ?").run(id);
};

export default {
  findAll,
  findById,
  create,
  update,
  deleteById,
};

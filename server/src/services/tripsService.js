import tripsRepository from "../repositories/tripsRepository.js";
import locationRepository from "../repositories/locationRepository.js";
import vendorsRepository from "../repositories/vendorsRepository.js";

const getAllTrips = () => {
  const trips = tripsRepository.findAll();

  return trips.map((trip) => ({
    ...trip,
    vendor: vendorsRepository.findById(trip.vendor_id) || null,
    pickup_location: locationRepository.findById(trip.pickup_location_id) || null,
    dropoff_location: locationRepository.findById(trip.dropoff_location_id) || null,
  }));
};

const getTripById = (id) => {
  return tripsRepository.findById(id);
};

const validateForeignKeys = (trip) => {
  if (trip.vendor_id !== undefined) {
    const vendor = vendorsRepository.findById(trip.vendor_id);
    if (!vendor) {
      throw new Error(`Vendor with id ${trip.vendor_id} not found`);
    }
  }

  if (trip.pickup_location_id !== undefined) {
    const pickupLocation = locationRepository.findById(trip.pickup_location_id);
    if (!pickupLocation) {
      throw new Error(
        `Pickup location with id ${trip.pickup_location_id} not found`,
      );
    }
  }

  if (trip.dropoff_location_id !== undefined) {
    const dropoffLocation = locationRepository.findById(
      trip.dropoff_location_id,
    );
    if (!dropoffLocation) {
      throw new Error(
        `Dropoff location with id ${trip.dropoff_location_id} not found`,
      );
    }
  }
};

const createTrip = (trip) => {
  validateForeignKeys(trip);
  return tripsRepository.create(trip);
};

const normalizeTripPatch = (tripData) => {
  const allowedFields = new Set([
    "vendor_id",
    "pickup_datetime",
    "dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "mta_tax",
    "pickup_location_id",
    "dropoff_location_id",
    "tip_amount",
    "fare_amount",
    "total_amount"
  ]);

  const patch = {};

  for (const [key, value] of Object.entries(tripData || {})) {
    if (!allowedFields.has(key)) continue;
    if (value === undefined) continue;
    patch[key] = value;
  }

  return patch;
};

const updateTrip = (id, tripData) => {
  const existing = tripsRepository.findById(id);
  if (!existing) return undefined;

  const patch = normalizeTripPatch(tripData);
  if (Object.keys(patch).length === 0) {
    throw new Error("No valid fields provided for update");
  }

  validateForeignKeys(patch);

  return tripsRepository.update(id, patch);
};

const deleteTrip = (id) => {
  const existing = tripsRepository.findById(Number(id));
  if (!existing) return false;

  tripsRepository.deleteById(Number(id));
  return true;
};

export default {
  getAllTrips,
  getTripById,
  createTrip,
  updateTrip,
  deleteTrip,
};

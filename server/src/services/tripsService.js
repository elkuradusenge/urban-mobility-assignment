import tripsRepository from "../repositories/tripsRepository.js";
import locationRepository from "../repositories/locationRepository.js";
import vendorsRepository from "../repositories/vendorsRepository.js";

const getAllTrips = () => {
  return tripsRepository.findAll();
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
  const id = tripsRepository.create(trip);
  return { ...trip, id };
};

const updateTrip = (id, tripData) => {
  const existing = tripsRepository.findById(id);
  if (!existing) return undefined;

  validateForeignKeys(tripData);

  tripsRepository.update(id, tripData);
  return { ...existing, ...tripData };
};

const deleteTrip = (id) => {
  const existing = tripsRepository.findById(id);
  if (!existing) return false;

  tripsRepository.deleteById(id);
  return true;
};

export default {
  getAllTrips,
  getTripById,
  createTrip,
  updateTrip,
  deleteTrip,
};

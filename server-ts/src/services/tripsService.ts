import tripsRepository from "../repositories/tripsRepository";
import locationRepository from "../repositories/locationRepository";
import vendorsRepository from "../repositories/vendorsRepository";
import { Trip } from "../types";

const getAllTrips = (): Trip[] => {
  return tripsRepository.findAll();
};

const getTripById = (id: number): Trip | undefined => {
  return tripsRepository.findById(id);
};

const validateForeignKeys = (trip: Partial<Trip>) => {
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

const createTrip = (trip: Trip): Trip => {
  validateForeignKeys(trip);
  const id = tripsRepository.create(trip);
  return { ...trip, id };
};

const updateTrip = (id: number, tripData: Partial<Trip>): Trip | undefined => {
  const existing = tripsRepository.findById(id);
  if (!existing) return undefined;

  validateForeignKeys(tripData);

  tripsRepository.update(id, tripData);
  return { ...existing, ...tripData };
};

const deleteTrip = (id: number): boolean => {
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

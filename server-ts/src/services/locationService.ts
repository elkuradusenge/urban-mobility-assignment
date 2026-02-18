import locationRepository from "../repositories/locationRepository";
import { Location } from "../types";

const getAllLocations = (): Location[] => {
  return locationRepository.findAll();
};

const getLocationById = (id: number): Location | undefined => {
  return locationRepository.findById(id);
};

const createLocation = (location: Location): Location => {
  const id = locationRepository.create(location);
  return { ...location, location_id: id };
};

const updateLocation = (
  id: number,
  locationData: Partial<Location>,
): Location | undefined => {
  const existing = locationRepository.findById(id);
  if (!existing) return undefined;

  locationRepository.update(id, locationData);
  return { ...existing, ...locationData };
};

const deleteLocation = (id: number): boolean => {
  const existing = locationRepository.findById(id);
  if (!existing) return false;

  locationRepository.deleteById(id);
  return true;
};

export default {
  getAllLocations,
  getLocationById,
  createLocation,
  updateLocation,
  deleteLocation,
};

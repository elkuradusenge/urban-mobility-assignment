import locationRepository from "../repositories/locationRepository.js";

const getAllLocations = () => {
  return locationRepository.findAll();
};

const getLocationById = (id) => {
  return locationRepository.findById(id);
};

const createLocation = (location) => {
  const id = locationRepository.create(location);
  return { ...location, location_id: id };
};

const updateLocation = (
  id,
  locationData,
) => {
  const existing = locationRepository.findById(id);
  if (!existing) return undefined;

  locationRepository.update(id, locationData);
  return { ...existing, ...locationData };
};

const deleteLocation = (id) => {
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

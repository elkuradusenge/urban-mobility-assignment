import locationRepository from "../repositories/locationRepository.js";

const getAllLocations = () => {
  return locationRepository.findAll();
};

const getLocationById = (id) => {
  return locationRepository.findById(id);
};

const createLocation = (location) => {
  return locationRepository.create(location);
};

const updateLocation = (
  id,
  locationData,
) => {
  const existing = locationRepository.findById(id);
  if (!existing) return undefined;

  return locationRepository.update(id, locationData);
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

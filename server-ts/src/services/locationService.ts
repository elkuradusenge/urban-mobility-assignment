import locationRepository from "../repositories/locationRepository";
import { Location } from "../types";

const getAllLocations = (): Location[] => {
  return locationRepository.findAll();
};

export default {
  getAllLocations,
};

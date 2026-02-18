import tripsRepository from "../repositories/tripsRepository";
import { Trip } from "../types";

const getAllTrips = (): Trip[] => {
  return tripsRepository.findAll();
};

export default {
  getAllTrips,
};

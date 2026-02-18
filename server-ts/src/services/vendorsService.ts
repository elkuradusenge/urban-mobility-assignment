import vendorsRepository from "../repositories/vendorsRepository";
import { Vendor } from "../types";

const getAllVendors = (): Vendor[] => {
  return vendorsRepository.findAll();
};

export default {
  getAllVendors,
};

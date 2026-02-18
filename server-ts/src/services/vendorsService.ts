import vendorsRepository from "../repositories/vendorsRepository";
import { Vendor } from "../types";

const getAllVendors = (): Vendor[] => {
  return vendorsRepository.findAll();
};

const getVendorById = (id: number): Vendor | undefined => {
  return vendorsRepository.findById(id);
};

const createVendor = (vendor: Vendor): Vendor => {
  const id = vendorsRepository.create(vendor);
  return { ...vendor, id };
};

const updateVendor = (
  id: number,
  vendorData: Partial<Vendor>,
): Vendor | undefined => {
  const existing = vendorsRepository.findById(id);
  if (!existing) return undefined;

  vendorsRepository.update(id, vendorData);
  return { ...existing, ...vendorData };
};

const deleteVendor = (id: number): boolean => {
  const existing = vendorsRepository.findById(id);
  if (!existing) return false;

  vendorsRepository.deleteById(id);
  return true;
};

export default {
  getAllVendors,
  getVendorById,
  createVendor,
  updateVendor,
  deleteVendor,
};

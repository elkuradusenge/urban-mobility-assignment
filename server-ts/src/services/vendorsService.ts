import vendorsRepository from "../repositories/vendorsRepository";
import { Vendor } from "../types";

const getAllVendors = (): Vendor[] => {
  return vendorsRepository.findAll();
};

const getVendorById = (id: number): Vendor | undefined => {
  return vendorsRepository.findById(id);
};

const createVendor = (vendor: Vendor): Vendor => {
  const existing = vendorsRepository.findByEmail(vendor.email);
  if (existing) {
    throw new Error(`Vendor with email ${vendor.email} already exists`);
  }
  const id = vendorsRepository.create(vendor);
  return { ...vendor, id };
};

const updateVendor = (
  id: number,
  vendorData: Partial<Vendor>,
): Vendor | undefined => {
  const existing = vendorsRepository.findById(id);
  if (!existing) return undefined;

  if (vendorData.email) {
    const existingEmail = vendorsRepository.findByEmail(vendorData.email);
    if (existingEmail && existingEmail.id !== id) {
      throw new Error(`Vendor with email ${vendorData.email} already exists`);
    }
  }

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

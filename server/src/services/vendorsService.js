import vendorsRepository from "../repositories/vendorsRepository.js";

const getAllVendors = () => {
  return vendorsRepository.findAll();
};

const getVendorById = (id) => {
  return vendorsRepository.findById(id);
};

const createVendor = (vendor) => {
  const existing = vendorsRepository.findByEmail(vendor.email);
  if (existing) {
    throw new Error(`Vendor with email ${vendor.email} already exists`);
  }
  const id = vendorsRepository.create(vendor);
  return { ...vendor, id };
};

const updateVendor = (
  id,
  vendorData,
) => {
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

const deleteVendor = (id) => {
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

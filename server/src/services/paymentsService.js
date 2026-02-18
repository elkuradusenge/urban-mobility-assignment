import paymentsRepository from "../repositories/paymentsRepository.js";

const getAllPayments = () => {
  return paymentsRepository.findAll();
};

const getPaymentById = (id) => {
  return paymentsRepository.findById(id);
};

const createPayment = (payment) => {
  const existing = paymentsRepository.findByName(payment.name);
  if (existing) {
    throw new Error(`Payment method ${payment.name} already exists`);
  }
  const id = paymentsRepository.create(payment);
  return { ...payment, id };
};

const updatePayment = (
  id,
  paymentData,
) => {
  const existing = paymentsRepository.findById(id);
  if (!existing) return undefined;

  if (paymentData.name) {
    const existingName = paymentsRepository.findByName(paymentData.name);
    if (existingName && existingName.id !== id) {
      throw new Error(`Payment method ${paymentData.name} already exists`);
    }
  }

  paymentsRepository.update(id, paymentData);
  return { ...existing, ...paymentData };
};

const deletePayment = (id) => {
  const existing = paymentsRepository.findById(id);
  if (!existing) return false;

  paymentsRepository.deleteById(id);
  return true;
};

export default {
  getAllPayments,
  getPaymentById,
  createPayment,
  updatePayment,
  deletePayment,
};

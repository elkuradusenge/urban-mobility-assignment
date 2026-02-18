import paymentsRepository from "../repositories/paymentsRepository";
import { Payment } from "../types";

const getAllPayments = (): Payment[] => {
  return paymentsRepository.findAll();
};

const getPaymentById = (id: number): Payment | undefined => {
  return paymentsRepository.findById(id);
};

const createPayment = (payment: Payment): Payment => {
  const id = paymentsRepository.create(payment);
  return { ...payment, id };
};

const updatePayment = (
  id: number,
  paymentData: Partial<Payment>,
): Payment | undefined => {
  const existing = paymentsRepository.findById(id);
  if (!existing) return undefined;

  paymentsRepository.update(id, paymentData);
  return { ...existing, ...paymentData };
};

const deletePayment = (id: number): boolean => {
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

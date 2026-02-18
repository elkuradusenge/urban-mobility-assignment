import paymentsRepository from "../repositories/paymentsRepository";
import { Payment } from "../types";

const getAllPayments = (): Payment[] => {
  return paymentsRepository.findAll();
};

export default {
  getAllPayments,
};

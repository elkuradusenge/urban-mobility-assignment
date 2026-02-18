import { db } from "../db/db";
import { Payment } from "../types";

const findAll = (): Payment[] => {
  return db.prepare("SELECT * FROM payments").all() as Payment[];
};

export default {
  findAll,
};

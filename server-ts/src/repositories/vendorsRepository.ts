import { db } from "../db/db";
import { Vendor } from "../types";

const findAll = (): Vendor[] => {
  return db.prepare("SELECT * FROM vendors").all() as Vendor[];
};

export default {
  findAll,
};

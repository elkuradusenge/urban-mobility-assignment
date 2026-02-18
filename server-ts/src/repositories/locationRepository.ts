import { db } from "../db/db";
import { Location } from "../types";

const findAll = (): Location[] => {
  return db.prepare("SELECT * FROM locations").all() as Location[];
};

export default {
  findAll,
};

import { db } from "../db/db";
import { Trip } from "../types";

const findAll = (): Trip[] => {
  return db.prepare("SELECT * FROM trips").all() as Trip[];
};

export default {
  findAll,
};

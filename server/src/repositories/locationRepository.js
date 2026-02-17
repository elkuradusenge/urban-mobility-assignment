const { db } = require('../db/db');

const findAll = () => {
    return db.prepare('SELECT * FROM locations').all();
};

module.exports = {
    findAll,
};

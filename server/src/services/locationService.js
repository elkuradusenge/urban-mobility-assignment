const locationRepository = require('../repositories/locationRepository');

const getAllLocations = () => {
    return locationRepository.findAll();
};

module.exports = {
    getAllLocations,
};

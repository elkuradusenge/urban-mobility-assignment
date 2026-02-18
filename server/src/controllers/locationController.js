const locationService = require('../services/locationService');

const getAllLocations = (req, res) => {
    try {
        const locations = locationService.getAllLocations();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(locations));
    } catch (error) {
        console.error(error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Internal Server Error' }));
    }
};

module.exports = {
    getAllLocations,
};

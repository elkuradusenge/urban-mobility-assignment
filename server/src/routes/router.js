const userController = require('../controllers/userController');

const router = async (req, res) => {
    const url = req.url;
    const method = req.method;

    console.log(`Incoming request: ${method} ${url}`);

    // CORS headers (optional but good practice)
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    if (url === '/users' && method === 'GET') {
        await userController.getUsers(req, res);
    } else if (url.match(/\/users\/\d+/) && method === 'GET') {
        const id = url.split('/')[2];
        await userController.getUser(req, res, id);
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Route not found' }));
    }
};

module.exports = router;

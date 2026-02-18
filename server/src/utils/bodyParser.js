const bodyParser = (req) => {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                if (!body) {
                    resolve({});
                } else {
                    resolve(JSON.parse(body));
                }
            } catch (error) {
                reject(error);
            }
        });
        req.on('error', (err) => {
            reject(err);
        });
    });
};

module.exports = bodyParser;

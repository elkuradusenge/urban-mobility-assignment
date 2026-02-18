# Data cleaning
[TBD]

# API
## How to start the server
- Clone the repo `git clone https://github.com/elkuradusenge/urban-mobility-assignment.git`
- Change the directory `cd server`
- With Node.js installed, install all the packages with `npm install`
- Run `node server.js` to start the server at `http://localhost:3000`
- On server start up the database will be initiated with tables and seed data. To demonstrate make a GET HTTP request to `/locations` to retrieve all locations in the database
- We are using `SQLite` as the database

## File structure
- Data cleaning is handled in `data` directory with Python
- The API will be built in the `server` directory with Node.js
- The web app will go in `client` directory with vanilla HTML, CSS and JavaScript
const Database = require("better-sqlite3");
const path = require('path');

const db = new Database("database.db");

const initDb = () => {
    // Locations Table
    db.prepare(`
        CREATE TABLE IF NOT EXISTS locations (
            location_id INTEGER PRIMARY KEY,
            borough TEXT,
            zone TEXT,
            service_zone TEXT
        )
    `).run();

    // Vendors Table
    db.prepare(`
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone_number TEXT
        )
    `).run();

    // Payments Table
    db.prepare(`
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    `).run();

    // Trips Table
    db.prepare(`
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            pickup_datetime TEXT,
            dropoff_datetime TEXT,
            passenger_count INTEGER,
            trip_distance REAL,
            mta_tax REAL,
            pickup_location_id INTEGER,
            dropoff_location_id INTEGER,
            tip_amount REAL,
            fare_amount REAL,
            total_amount REAL,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id),
            FOREIGN KEY (pickup_location_id) REFERENCES locations(location_id),
            FOREIGN KEY (dropoff_location_id) REFERENCES locations(location_id)
        )
    `).run();

    console.log("Database tables initialized.");
};

module.exports = {
    db,
    initDb
};

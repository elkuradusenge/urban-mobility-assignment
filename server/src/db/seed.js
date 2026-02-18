import { db } from "./db.js";

export const seedIfEmpty = () => {
  console.log("Checking if database needs seeding...");

  // 1. Locations
  const locationsCount = (
    db.prepare("SELECT count(*) as c FROM locations").get()
  ).c;
  if (locationsCount === 0) {
    console.log("Seeding locations...");
    const insertLocation = db.prepare(`
            INSERT INTO locations (location_id, borough, zone, service_zone)
            VALUES (?, ?, ?, ?)
        `);

    // Using partial data for brevity in code, but in a real scenario, this would be the full list
    const locations = [
      {
        location_id: 1,
        borough: "EWR",
        zone: "Newark Airport",
        service_zone: "EWR",
      },
      {
        location_id: 2,
        borough: "Queens",
        zone: "Jamaica Bay",
        service_zone: "Boro Zone",
      },
      {
        location_id: 3,
        borough: "Bronx",
        zone: "Allerton/Pelham Gardens",
        service_zone: "Boro Zone",
      },
      {
        location_id: 4,
        borough: "Manhattan",
        zone: "Alphabet City",
        service_zone: "Yellow Zone",
      },
      {
        location_id: 5,
        borough: "Staten Island",
        zone: "Arden Heights",
        service_zone: "Boro Zone",
      },
      {
        location_id: 6,
        borough: "Staten Island",
        zone: "Arrochar/Fort Wadsworth",
        service_zone: "Boro Zone",
      },
      {
        location_id: 7,
        borough: "Queens",
        zone: "Astoria",
        service_zone: "Boro Zone",
      },
      {
        location_id: 8,
        borough: "Queens",
        zone: "Astoria Park",
        service_zone: "Boro Zone",
      },
      {
        location_id: 9,
        borough: "Queens",
        zone: "Auburndale",
        service_zone: "Boro Zone",
      },
      {
        location_id: 10,
        borough: "Queens",
        zone: "Baisley Park",
        service_zone: "Boro Zone",
      },
      {
        location_id: 11,
        borough: "Brooklyn",
        zone: "Bath Beach",
        service_zone: "Boro Zone",
      },
      {
        location_id: 12,
        borough: "Manhattan",
        zone: "Battery Park",
        service_zone: "Yellow Zone",
      },
      {
        location_id: 13,
        borough: "Manhattan",
        zone: "Battery Park City",
        service_zone: "Yellow Zone",
      },
      {
        location_id: 14,
        borough: "Brooklyn",
        zone: "Bay Ridge",
        service_zone: "Boro Zone",
      },
      {
        location_id: 15,
        borough: "Queens",
        zone: "Bay Terrace/Fort Totten",
        service_zone: "Boro Zone",
      },
      {
        location_id: 16,
        borough: "Queens",
        zone: "Bayside",
        service_zone: "Boro Zone",
      },
      {
        location_id: 17,
        borough: "Brooklyn",
        zone: "Bedford",
        service_zone: "Boro Zone",
      },
      {
        location_id: 18,
        borough: "Bronx",
        zone: "Bedford Park",
        service_zone: "Boro Zone",
      },
      {
        location_id: 19,
        borough: "Queens",
        zone: "Bellerose",
        service_zone: "Boro Zone",
      },
      {
        location_id: 20,
        borough: "Bronx",
        zone: "Belmont",
        service_zone: "Boro Zone",
      },
    ];

    const insertLocationsTransaction = db.transaction((locs) => {
      for (const l of locs) {
        insertLocation.run(l.location_id, l.borough, l.zone, l.service_zone);
      }
    });
    insertLocationsTransaction(locations);
    console.log("Seeded 20 locations.");
  } else {
    console.log("Locations table already has data. Skipping.");
  }

  // 2. Vendors
  const vendorsCount = (
    db.prepare("SELECT count(*) as c FROM vendors").get()
  ).c;
  if (vendorsCount === 0) {
    console.log("Seeding vendors...");
    const insertVendor = db.prepare(`
            INSERT INTO vendors (id, name, email, phone_number)
            VALUES (?, ?, ?, ?)
        `);

    const vendors = [
      {
        id: 1,
        name: "Michael Johnson",
        email: "michael.johnson@nycdispatch.com",
        phone_number: "+1-212-555-0141",
      },
      {
        id: 2,
        name: "Sarah Williams",
        email: "sarah.williams@metrotaxi.co",
        phone_number: "+1-646-555-0182",
      },
      {
        id: 3,
        name: "David Martinez",
        email: "d.martinez@citycabservices.com",
        phone_number: "+1-917-555-0133",
      },
      {
        id: 4,
        name: "Jessica Brown",
        email: "jessica.brown@urbanfleet.net",
        phone_number: "+1-718-555-0174",
      },
      {
        id: 5,
        name: "Christopher Davis",
        email: "chris.davis@nytransport.org",
        phone_number: "+1-347-555-0155",
      },
      {
        id: 6,
        name: "Amanda Garcia",
        email: "amanda.garcia@taxilinkny.com",
        phone_number: "+1-929-555-0196",
      },
      {
        id: 7,
        name: "Daniel Rodriguez",
        email: "daniel.rodriguez@yellowfleetny.com",
        phone_number: "+1-212-555-0167",
      },
      {
        id: 8,
        name: "Emily Wilson",
        email: "emily.wilson@metrodispatchny.com",
        phone_number: "+1-646-555-0128",
      },
      {
        id: 9,
        name: "Matthew Anderson",
        email: "m.anderson@cityridegroup.com",
        phone_number: "+1-917-555-0119",
      },
      {
        id: 10,
        name: "Olivia Thomas",
        email: "olivia.thomas@nyctaxico.com",
        phone_number: "+1-718-555-0100",
      },
    ];

    const insertVendorsTransaction = db.transaction((vs) => {
      for (const v of vs) {
        insertVendor.run(v.id, v.name, v.email, v.phone_number);
      }
    });
    insertVendorsTransaction(vendors);
    console.log("Seeded 10 vendors.");
  } else {
    console.log("Vendors table already has data. Skipping.");
  }

  // 3. Payments
  const paymentsCount = (
    db.prepare("SELECT count(*) as c FROM payments").get()
  ).c;
  if (paymentsCount === 0) {
    console.log("Seeding payments...");
    const insertPayment = db.prepare(`
            INSERT INTO payments (id, name)
            VALUES (?, ?)
        `);

    const payments = [
      { id: 1, name: "Mastercard" },
      { id: 2, name: "Visa" },
      { id: 3, name: "Cash" },
      { id: 4, name: "MoMo" },
      { id: 5, name: "Unknown" },
    ];

    const insertPaymentsTransaction = db.transaction((ps) => {
      for (const p of ps) {
        insertPayment.run(p.id, p.name);
      }
    });
    insertPaymentsTransaction(payments);
    console.log("Seeded 5 payment methods.");
  } else {
    console.log("Payments table already has data. Skipping.");
  }

  // 4. Trips
  const tripsCount = (
    db.prepare("SELECT count(*) as c FROM trips").get()
  ).c;
  if (tripsCount === 0) {
    console.log("Seeding trips...");
    const insertTrip = db.prepare(`
            INSERT INTO trips (
                vendor_id, pickup_datetime, dropoff_datetime, passenger_count, 
                trip_distance, mta_tax, pickup_location_id, dropoff_location_id, 
                tip_amount, fare_amount, total_amount
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

    const trips = []; // ID is autoincrement
    for (let i = 1; i <= 10; i++) {
      const fare = parseFloat((Math.random() * 20 + 5).toFixed(2));
      const tip = parseFloat((Math.random() * 5).toFixed(2));
      const tax = 0.5;
      const total = parseFloat((fare + tip + tax).toFixed(2));

      trips.push({
        vendor_id: Math.floor(Math.random() * 10) + 1,
        pickup_datetime: `2019-01-01 00:${10 + i}:00`,
        dropoff_datetime: `2019-01-01 00:${20 + i}:00`,
        passenger_count: Math.floor(Math.random() * 4) + 1,
        trip_distance: parseFloat((Math.random() * 10).toFixed(2)),
        mta_tax: tax,
        pickup_location_id: Math.floor(Math.random() * 20) + 1,
        dropoff_location_id: Math.floor(Math.random() * 20) + 1,
        tip_amount: tip,
        fare_amount: fare,
        total_amount: total,
      });
    }

    const insertTripsTransaction = db.transaction((ts) => {
      for (const t of ts) {
        insertTrip.run(
          t.vendor_id,
          t.pickup_datetime,
          t.dropoff_datetime,
          t.passenger_count,
          t.trip_distance,
          t.mta_tax,
          t.pickup_location_id,
          t.dropoff_location_id,
          t.tip_amount,
          t.fare_amount,
          t.total_amount,
        );
      }
    });
    insertTripsTransaction(trips);
    console.log("Seeded 10 trips.");
  } else {
    console.log("Trips table already has data. Skipping.");
  }

  console.log("Database verification/seeding completed.");
};

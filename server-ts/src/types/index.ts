export interface Location {
  location_id: number;
  borough: string;
  zone: string;
  service_zone: string;
}

export interface Vendor {
  id: number;
  name: string;
  email: string;
  phone_number: string;
}

export interface Payment {
  id: number;
  name: string;
}

export interface Trip {
  id: number;
  vendor_id: number;
  pickup_datetime: string;
  dropoff_datetime: string;
  passenger_count: number;
  trip_distance: number;
  mta_tax: number;
  pickup_location_id: number;
  dropoff_location_id: number;
  tip_amount: number;
  fare_amount: number;
  total_amount: number;
}

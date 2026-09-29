CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    last_updated TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id VARCHAR(50) PRIMARY KEY,
    vehicle_id VARCHAR(50) REFERENCES vehicles(vehicle_id),
    sensor_type VARCHAR(20) CHECK (sensor_type IN ('battery', 'airbag', 'fuel')),
    installation_date DATE,
    last_calibration TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS battery_events (
    reading_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    voltage FLOAT NOT NULL,
    charge_level INTEGER NOT NULL,
    temperature FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    unit_voltage VARCHAR(10) DEFAULT 'V',
    unit_temperature VARCHAR(10) DEFAULT 'Celsius'
);

CREATE TABLE IF NOT EXISTS airbag_events (
    event_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    activated BOOLEAN NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE IF NOT EXISTS fuel_events (
    reading_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    level FLOAT NOT NULL,
    unit VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE actuators (
    actuator_id VARCHAR(50) PRIMARY KEY,
    actuator_name VARCHAR(100) NOT NULL,
    sensor_type VARCHAR(50),
    description TEXT,
    code VARCHAR(250) NOT NULL
);

INSERT INTO vehicles (vehicle_id, make, model, year, last_updated)
VALUES ('car001', 'Tesla', 'Model 3', 2023, NOW());

INSERT INTO sensors (sensor_id, vehicle_id, sensor_type, installation_date, last_calibration)
VALUES ('battery001', 'car001', 'battery', '2023-01-15', '2023-06-01');

INSERT INTO sensors (sensor_id, vehicle_id, sensor_type, installation_date, last_calibration)
VALUES ('airbag001', 'car001', 'airbag', '2023-01-15', '2023-01-15');

INSERT INTO sensors (sensor_id, vehicle_id, sensor_type, installation_date, last_calibration)
VALUES ('fuel001', 'car001', 'fuel', '2023-01-15', '2023-06-01');

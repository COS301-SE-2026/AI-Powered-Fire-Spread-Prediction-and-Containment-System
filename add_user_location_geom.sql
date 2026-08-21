ALTER TABLE users
    ADD COLUMN location_geom geometry(Point, 4326);

CREATE INDEX idx_users_location_geom
    ON users
    USING GIST (location_geom);
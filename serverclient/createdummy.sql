-- create a PostgreSQL table with index of 5 types of data
--
-- cleanup old table
DROP TABLE topictable CASCADE;

-- create roles
CREATE ROLE dbcreator WITH PASSWORD 'nifti';
CREATE ROLE dbuser WITH PASSWORD 'nifti';
ALTER ROLE dbuser WITH LOGIN;
ALTER ROLE dbcreator WITH LOGIN;

-- create the dummy table for test
CREATE TABLE topictable (
            "id" oid PRIMARY KEY,
            "topic" text DEFAULT NULL,
            "type" text DEFAULT NULL,
            "timestamp" int8 DEFAULT NULL,
            "target" oid DEFAULT NULL
            )
WITH (OIDS=FALSE);
ALTER TABLE topictable OWNER TO "dbuser";
GRANT ALL PRIVILEGES ON topictable TO dbcreator;
GRANT SELECT ON topictable TO dbuser;

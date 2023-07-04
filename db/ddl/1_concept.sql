DO $$ BEGIN
    CREATE TYPE main.enum_difficulty AS ENUM ('Low', 'Medium', 'High');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS main.concept (
    ID SERIAL PRIMARY KEY,
    CONCEPT VARCHAR(32),
    MEANING VARCHAR(128),
    DIFFICULTY main.enum_difficulty NOT NULL,
);

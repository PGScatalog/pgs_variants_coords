CREATE TABLE IF NOT EXISTS "variant" (
    varname VARCHAR(50) PRIMARY KEY,
    current_varname VARCHAR(50) DEFAULT NULL,
    source_rest_api BOOLEAN NOT NULL DEFAULT 0  
);
-- CREATE INDEX current_varname_idx ON variant (current_varname);

CREATE TABLE IF NOT EXISTS "variant_coords" (
    current_varname VARCHAR(50) NOT NULL,
    chr VARCHAR(50) NOT NULL,
    start INT NOT NULL,
    end INT NOT NULL,
    alleles TEXT NOT NULL,
    CONSTRAINT fk_column
        FOREIGN KEY (current_varname)
        REFERENCES variant (current_varname)
        ON DELETE CASCADE,
    PRIMARY KEY (current_varname, chr, start)
);
-- CREATE INDEX current_varname_idx2 ON variant_coords (current_varname);
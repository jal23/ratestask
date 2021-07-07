CREATE TABLE ports (
    code text NOT NULL,
    name text NOT NULL,
    parent_slug text NOT NULL
);
CREATE TABLE prices (
    orig_code text NOT NULL,
    dest_code text NOT NULL,
    day date NOT NULL,
    price integer NOT NULL
);
CREATE TABLE regions (
    slug text NOT NULL,
    name text NOT NULL,
    parent_slug text
);

ALTER TABLE ONLY ports
    ADD CONSTRAINT ports_pkey PRIMARY KEY (code);

ALTER TABLE ONLY regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (slug);

ALTER TABLE ONLY ports
    ADD CONSTRAINT ports_parent_slug_fkey FOREIGN KEY (parent_slug) REFERENCES regions(slug);

ALTER TABLE ONLY prices
    ADD CONSTRAINT prices_dest_code_fkey FOREIGN KEY (dest_code) REFERENCES ports(code);

ALTER TABLE ONLY prices
    ADD CONSTRAINT prices_orig_code_fkey FOREIGN KEY (orig_code) REFERENCES ports(code);

ALTER TABLE ONLY regions
    ADD CONSTRAINT regions_parent_slug_fkey FOREIGN KEY (parent_slug) REFERENCES regions(slug);


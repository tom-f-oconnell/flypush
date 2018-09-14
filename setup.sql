/* TODO way to automate database creation and population in same sql script?
  or need two connections?
  (what CREATE_db_and_role.sql is doing + what this script is doing)
 
\c flypush
 */

/* TODO CREATE 'lab' user, for common stocks? */
CREATE TABLE IF NOT EXISTS people (
    nickname text PRIMARY KEY,
    /* maybe normalize these somewhere if going to use this field for automated
     * emails, texts, etc */
    email text,
    mobile_phone text,
    alt_phone text,
    default_num_seed_males smallint CHECK (default_num_seed_males > 0),
    default_num_seed_females smallint CHECK (default_num_seed_females > 0),
    default_add_yeast boolean
    /* TODO provide defaults for other values we will want input on. maybe
     * protocols? make their handling generic? */
);

CREATE TABLE IF NOT EXISTS rooms (
    name text PRIMARY KEY
    /* TODO sensor name for importing from sensorpush csv? */
    /* TODO id in incubator log dump? */
);

/* TODO deny all permissions besides insert on history tables? possible? */
CREATE TABLE IF NOT EXISTS room_history (
    updated timestamptz(0) PRIMARY KEY,
    name text REFERENCES rooms (name) NOT NULL,
    /* To discourage people from accidentally entering temperatures in other
     * units. 40C for any length should kill flies. */
    set_temp_celsius real CHECK (set_temp_celsius < 50),
    measured_temp_celsius real CHECK (measured_temp_celsius < 50),
    light_on_time timestamptz(0),
    light_off_time timestamptz(0),
    set_humidity real CONSTRAINT set_humidity_is_percent
        CHECK (set_humidity >= 0 and set_humidity <= 100),
    measured_humidity real CONSTRAINT measured_humidity_is_percent
        CHECK (measured_humidity >= 0 and measured_humidity <= 100),
    /*
    sound_spectrogram 
    light_spectrogram
    */
    /* specify locations within a room? e.g. shelves & spaces per shelves? */
    /* TODO force certain media type on picture or specify as metadata here? */
    pictures bytea[],
    notes text
);

/* TODO TODO CREATE view of tables w/ separate history, to present them as one
 * table? and hide real tables somehow? */
/* Boxes of fly vials and / or bottles. */
CREATE TABLE IF NOT EXISTS boxes (
    label text PRIMARY KEY,
    owner text REFERENCES people (nickname)
);

CREATE TABLE IF NOT EXISTS box_history (
    updated timestamptz(0) PRIMARY KEY,
    label text REFERENCES boxes (label) NOT NULL,

    /* TODO TODO how do i want to reference room, if that field isn't unique in
     * room table? make separate "rooms" table w/ just room name PK, and
     * reference it w/ foreign key both here and in new "room_history" table? */
    room text REFERENCES rooms (name),

    /* TODO make enum if still supporting
    shelf_number
    front_or_back
    */

    notes text
);

CREATE TABLE IF NOT EXISTS fly_lines (
    id SERIAL PRIMARY KEY,

    source text,
    source_contact text,
    /* To include creation */
    receive_date date,

    /* one line identifier # to normalize? */
    /* TODO constrain to valid IDs as much as possible */
    flybase_id text UNIQUE,
    /*
    bdsc_stock_no text
    dgrc_no text
    */
    /* so kyoto just uses DGRC numbers?
    kyoto_stock_no */
    
    description text UNIQUE,

    nickname text UNIQUE,

    /* TODO can use first second third? array? 'first' a reserved word?
    one
    two
    three

    try to figure out how flybase / kyoto do it?
    */

    last_flipped timestamptz(0),
    notes text,

    dead boolean
);


CREATE TYPE container_type AS ENUM ('vial', 'bottle');

CREATE TABLE IF NOT EXISTS fly_containers (
    id SERIAL PRIMARY KEY,
    owner text REFERENCES people (nickname) NOT NULL,
    box text REFERENCES boxes (label),

    /* better name? */
    kind container_type NOT NULL,

    seeded_at timestamptz(0) NOT NULL,

    /* TODO defaults? per person defaults? 
       table to give protocols diff names? */
    num_seed_females smallint CHECK (num_seed_females > 0),
    num_seed_males smallint CHECK (num_seed_males > 0),

    added_yeast boolean,

    female_line integer REFERENCES fly_lines (id),
    male_line integer REFERENCES fly_lines (id),

    female_container integer REFERENCES fly_containers (id),
    male_container integer REFERENCES fly_containers (id),

    started_at timestamptz(0),

    /* list / array (length = # days in cycle?) */
    cleared_at timestamptz(0),

    notes text
);

CREATE TABLE IF NOT EXISTS container_history (
    taken_at timestamptz(0) PRIMARY KEY,
    container integer REFERENCES fly_containers (id),
    pic bytea
);

/* Groups of flies that will ultimately serve as experimental animals. */
/* TODO how to handle splitting into multiple vials? change ID on each split?
   define to need to be two separate IDs from that point on?
 
   indicate continuity... (ref source groups? just one?) */
CREATE TABLE IF NOT EXISTS fly_groups (
    id SERIAL PRIMARY KEY,
    fly_container integer REFERENCES fly_containers (id),

    /* Range of dates over which flies were allowed to ecclose, before being
     * transferred. */
    /* TODO more precision? convention for picking start & end dates? 
      end date defined as clear, right? rename? */
    eclosion_start_date date,
    eclosion_end_date date,

    starved_at timestamptz(0),
    /* TODO sep table to manage protocols? give each a name / version, then
     * description? */
    starvation_protocol text,
    new_food_at timestamptz(0),
    new_food_protocol text,

    /*
    cold_anesthesia_at
    co2_anesthesia_at
    */

    notes text
);

/* TODO how do i want to represent crosses? */

CREATE TABLE IF NOT EXISTS experiment_series (
    id SERIAL PRIMARY KEY,
    name text UNIQUE NOT NULL,
    owner text REFERENCES people (nickname),
    question text,
    experimenter text REFERENCES people (nickname)
);

/* TODO consult w/ david about design of exp / exp_series? */
CREATE TABLE IF NOT EXISTS experiments (
    /* TODO TODO maybe just make diff pk and determine experiment series from
     * things that have multiple dirs for the same experiment pk (to avoid
     * having to inherit values from other table)? */
    /* TODO TODO maybe open a browser so user can select a path on NAS for dir?
       (assuming this site is being run on the same server, as we may want it
        anyway...) */
    dir text PRIMARY KEY,
    name text,
    owner text REFERENCES people (nickname),
    /* TODO inherit purpose from choice_experiment_series if reference to that
     * is not null */
    question text,
    notes text,
    experiment_series integer REFERENCES experiment_series (id)
    /* TODO maybe extend to add stimulus_params (as all yaml, or subfields)
    in stimuli */
);

CREATE TABLE IF NOT EXISTS rigs (
    id SERIAL PRIMARY KEY,
    room text REFERENCES rooms (name),
    date_made date,
    made_by text REFERENCES people (nickname),
    pictures bytea[],
    notes text
    /* TODO add this in extension of this table, added in olfactometry
    flow_diagram
    */
);

CREATE TABLE IF NOT EXISTS components (
    id SERIAL PRIMARY KEY,
    date_made date,
    made_by text REFERENCES people (nickname),
    /* TODO impose additional constraints on this (and other) path fields? */
    repository text,
    filename text,
    git_version text,
    pictures bytea[]
);

CREATE TABLE IF NOT EXISTS runs (
    /* TODO maybe derive dir id from this? */
    run_timestamp timestamptz(0) PRIMARY KEY,
    experiment text REFERENCES experiments (dir),
    rig integer REFERENCES rigs (id)
);

/* Metadata to control visibility and behavior of tables / fields in web
 * interface */
/* TODO use variable for flypush_tables, if that's common practice */
/* TODO also include metadata to group by which package installed the tables +
 * order for display

(+AT LEAST TWO GROUPS OF IMPORTANCE: rigs, boxes, components, (rooms?) under
 lesser?)*/
CREATE TABLE IF NOT EXISTS flypush_tables (
    table_name text PRIMARY KEY,
    website_visible boolean DEFAULT TRUE,
    website_editable boolean DEFAULT TRUE
);
DELETE FROM flypush_tables WHERE table_name in ('flypush_tables', 'runs');
/* TODO maybe move interacting w/ this table to a 'settings' page, under a
 * different menu (link off to the side)? */
INSERT INTO flypush_tables VALUES ('flypush_tables', FALSE, FALSE);
/* TODO was originally going to just display runs, but maybe move it so all runs
 * display under experiments */
INSERT INTO flypush_tables VALUES ('runs', FALSE, FALSE);


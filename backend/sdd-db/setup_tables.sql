DROP DATABASE IF EXISTS sdd;
CREATE DATABASE sdd;
USE sdd;

/* contains weather information since 2007-01-01 */
DROP TABLE IF EXISTS weather;
CREATE TABLE weather (
  id INT UNSIGNED auto_increment PRIMARY KEY,
  temp DOUBLE NULL,
  temp_min DOUBLE NULL,
  temp_max DOUBLE NULL,
  rainfall DOUBLE NULL,
  snowfall DOUBLE NULL,
  snowdepth DOUBLE NULL,
  winddirection DOUBLE NULL,
  windspeed DOUBLE NULL,
  peakgust DOUBLE NULL,
  sunshine DOUBLE NULL,
  pressure DOUBLE NULL,
  district_id VARCHAR(32) NOT NULL,
  dt DATETIME NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX(district_id),
  INDEX(dt)
)

/* Contains meta information for all amtliche Gemeindeschlüssel */
DROP TABLE IF EXISTS locations;
CREATE TABLE locations (
  district_id VARCHAR(5) PRIMARY KEY, /* district_id */
  district VARCHAR(128) NOT NULL,
  district_type VARCHAR(128) NOT NULL,
  state_id VARCHAR(32) NOT NULL, /* "BW" "B" etc */
  state VARCHAR(128) NOT NULL, /* "Baden-Württemberg" */
  country_id VARCHAR(32) NOT NULL, /* "DE" */
  country VARCHAR(128) NOT NULL, /* "Deutschland" */
  lat DOUBLE NOT NULL,
  lon DOUBLE NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
) CHARACTER SET utf8;

/* Contains the available score names */
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
  name VARCHAR(64) PRIMARY KEY,
  desc_short TEXT NOT NULL,
  desc_long TEXT NOT NULL,
  contributors TEXT NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8;


DROP TABLE IF EXISTS scores_meta;
CREATE TABLE scores_meta (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  district_id VARCHAR(32) NOT NULL, /* regional identifier */
  category VARCHAR(64) NOT NULL, /* which source */
  meta TEXT NULL, /* stringified JSON dump with additional characteristics */
  description TEXT NULL, /* BHF Name, Webcam Standort, etc */
  source_id VARCHAR(128), /* Dient dazu innerhalb eines districtes Quellen zu unterscheiden. Bspw. "Webcam Marktplatz" */
  INDEX(category),
  INDEX(district_id),
  UNIQUE(district_id, category, source_id) /* Meta Daten sind zeitunabhängig */
);



/* Contains the actual data */
DROP TABLE IF EXISTS scores;
CREATE TABLE  scores (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
  dt DATETIME NOT NULL,
  score_value DOUBLE NOT NULL,
  reference_value DOUBLE NULL DEFAULT 0, /* expceted value without corona */
  category VARCHAR(64) NOT NULL,
  district_id VARCHAR(32) NOT NULL, /* regional identifier */
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  meta_id INT UNSIGNED NOT NULL,
  INDEX(category),
  INDEX(dt),
  INDEX(district_id)
) CHARACTER SET utf8;



DROP TABLE IF EXISTS measures;
CREATE TABLE measures (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY, /* no meaning */
  dt_announcement DATETIME NOT NULL, /* Datetime of publication */
  dt_start_action DATETIME NOT NULL, /* Datetime when action takes into effect */
  dt_end_action DATETIME NULL, /* Datetime when action is supposed to end */
  desc_short TEXT NOT NULL, /* Short description. */
  desc_long TEXT NOT NULL, /* Long description */
  level1_id_announced VARCHAR(32) NOT NULL, /* country code of place where measure was announced*/
  level2_id_announced VARCHAR(32) NOT NULL, /* county code of place where measure was announced*/
  level3_id_announced VARCHAR(32) NOT NULL, /* district code of place where measure was announced*/
  level1_id_action VARCHAR(32) NULL, /* country code if action is applicable */
  level2_id_action VARCHAR(32) NULL, /* county code if action is applicable */
  level3_id_action VARCHAR(32) NULL, /* district code if action is applicable */
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8;



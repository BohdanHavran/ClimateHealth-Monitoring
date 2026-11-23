-- Bootstrap for a NEW empty local MySQL volume only.
-- Not a migration and not authorized for an existing database.
-- Docker entrypoint has selected MYSQL_DATABASE before running this file.
CREATE TABLE IF NOT EXISTS climate_data (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  year SMALLINT NOT NULL,
  month TINYINT UNSIGNED NOT NULL,
  avg_temp DOUBLE NULL,
  solar_irradiance DOUBLE NULL,
  humidity DOUBLE NULL,
  INDEX idx_period (year, month),
  CONSTRAINT chk_month CHECK (month BETWEEN 1 AND 12)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS hri_impacts (
  level VARCHAR(10) PRIMARY KEY,
  impact TEXT,
  recommendations TEXT,
  diseases TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ua_places (
  geoname_id BIGINT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  asciiname VARCHAR(200) NULL,
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  feature_class CHAR(1) NULL,
  feature_code VARCHAR(10) NULL,
  admin1_code VARCHAR(20) NULL,
  admin2_code VARCHAR(80) NULL,
  population BIGINT NULL,
  timezone VARCHAR(40) NULL,
  modified_date DATE NULL,
  INDEX idx_lat (latitude),
  INDEX idx_lon (longitude),
  INDEX idx_pop (population),
  FULLTEXT KEY ft_name (name, asciiname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS hri_cache (
  lat DOUBLE NOT NULL,
  lon DOUBLE NOT NULL,
  fetched_at DATETIME NOT NULL,
  avg_temp DOUBLE NOT NULL,
  solar DOUBLE NOT NULL,
  humidity DOUBLE NOT NULL,
  hri DOUBLE NOT NULL,
  PRIMARY KEY (lat, lon),
  INDEX idx_fetched (fetched_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Descriptions are not observed medical labels or calibrated clinical advice.
INSERT IGNORE INTO hri_impacts (level, impact, recommendations, diseases) VALUES
('low', 'Низький індекс за нечіткими правилами.', 'Оцініть актуальні умови та офіційні повідомлення.', 'Медичний прогноз не розраховано.'),
('medium', 'Середній індекс за нечіткими правилами.', 'Оцініть актуальні умови та офіційні повідомлення.', 'Медичний прогноз не розраховано.'),
('high', 'Високий індекс за нечіткими правилами.', 'Оцініть актуальні умови та офіційні повідомлення.', 'Медичний прогноз не розраховано.');

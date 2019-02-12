CREATE TABLE commit_api (
  commit_sha TINYTEXT NOT NULL,
  api_version TINYINT NOT NULL
);

CREATE TABLE commit_permissions (
  commit_sha TINYTEXT NOT NULL,
  permission_id INT NOT NULL
);

CREATE TABLE permissions (
  id INT PRIMARY KEY,
  name TEXT NOT NULL
);
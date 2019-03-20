CREATE TABLE commit_api (
  commit_sha      varchar(64) NOT NULL,
  api_version     TINYINT NOT NULL,
  UNIQUE KEY      (commit_sha)
);

CREATE TABLE commit_permissions (
  commit_sha      varchar(64) NOT NULL,
  permission_id   INT NOT NULL
);

CREATE TABLE permissions (
  id              INT unsigned NOT NULL AUTO_INCREMENT,
  name            varchar(256) NOT NULL,
  PRIMARY KEY     (id),
  UNIQUE KEY      (name)
);
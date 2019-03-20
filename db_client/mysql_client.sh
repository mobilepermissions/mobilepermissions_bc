# TODO move to config file
db_user="root"
db_db="research"

export MYSQL_PWD=root


function insert_test {
  echo "Hello"
}

function insert_commit_info {
  ### Inserts information of a commit into the database
  ### Parameters
  # $1 commit_sha
  # $2 min_api
  # $3+ permissions (varargs)
  commit_sha=$1
  min_api=$2
  shift;shift;
  insert_commit_api $commit_sha $min_api
  
  for permission in "$@"; do
    insert_permission $commit_sha $permission
  done

}

function insert_commit_api {
  ### Inserts just the commit api version into the database
  # $1 commit_sha
  # $2 min_api
  
  r=`mysql -u$db_user $db_db -e "INSERT INTO commit_api (commit_sha,api_version) VALUES ('$1',$2);"`
}

function insert_permission {
  ### Inserts a permission into the database
  # $1 commit_sha
  # $2 permission
  
  # Try to insert permission, then get id
  mysql -u$db_user $db_db -e "INSERT IGNORE INTO permissions (name) VALUES ('$2');"
  perm_id=`mysql -u$db_user $db_db -s -N -e "SELECT id FROM permissions WHERE name='$2';"`
  
  # Add the permission to the commit
  mysql -u$db_user $db_db -e "INSERT INTO commit_permissions (commit_sha, permission_id) VALUES ('$1','$perm_id');"
}

insert_commit_info TEST_COMMIT_SHA 21 PERM1 PERM2 PERM3
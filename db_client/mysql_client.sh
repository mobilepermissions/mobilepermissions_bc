# TODO move to config file
db_user="root"
db_pass="root"
db_db="research"


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
  
  echo "INSERT INTO commit_api (commit_sha,api_version) VALUES ('$1',$2);" | mysql -u$db_user -p$dp_pass $db_db;
}

function insert_permission {
  ### Inserts a permission into the database
  # $1 commit_sha
  # $2 permission
  
  # TODO
}
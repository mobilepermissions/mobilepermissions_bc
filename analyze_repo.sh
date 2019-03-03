### This file contains scripts for analyzing a single git repository

### Usage
### 	`analyze_repo [-r|--repo repo_name] [-d|--directory cloned_repo_dir]`

### Includes
.   db_client/sqlite_client.sh



### Collected Repos root
	gh_repos_dir="test_repos"
  
### Repo Versions root
  version_root="versions"
  
### Python Scripts
  python_runtime="python3"
  python_parse_manifest="python/parse_manifest.py"
  python_locate_manifests="python/locate_manifests.py"
	
### Logs
	gh_log_dir="gh_logs"
	gh_log_file_clone="$gh_log_dir/clone.txt"
  
### Get params
	while [[ $# -gt 0 ]]
	do
	key="$1"

	case $key in
		-r|--repo)
		repo_name="$2"
		shift # past argument
		shift # past value
		;;
		-d|--directory)
		repo_dir="$2"
		shift # past argument
		shift # past value
		;;
    -tm|--test-manifest)
    tm_arg=1
		shift # past argument
		;;
	esac
	done
	
function repo_to_dir {
	c_d=${1//\//-}
	echo "$gh_repos_dir/$c_d"
}
	
function instantiate_repo {
	### Pulls the repository specified as a parameter
	gh_url="https://u:p@github.com/$repo_name.git"
	
	# Make the destination for the repo
	clone_dir=`repo_to_dir $repo_name`
	
	# Clone repsitory and return duration of operation in seconds
	git clone --quiet $gh_url $clone_dir
  
  # Set the repo_dir and begin analysis
  repo_dir=$clone_dir
}

function get_releases {
	### Gets the releases for the repo_name
	
  cd $repo_dir
  
    for tag in `git tag`; do
  
      output_loc="../../$version_root/$repo_dir/$tag"
      attach_tag_head $output_loc $tag
      sdk_version=`get_branch_sdk_version $output_loc`
      echo "Found sdk version: $sdk_version"
     
    done
    
    cd ../..
}

function attach_tag_head {
  ### Parameters
  # $1 output_location
  # $2 tag to checkout the head of
  mkdir -p "$output_loc"
  
  cd $repo_dir
      
    git checkout --quiet $2
    git --work-tree=$1 checkout --quiet HEAD -- .
  
  cd ../..
  
  echo "Checked out head of tag: $2"
}

function get_branch_sdk_version {
  ### Parameters
  # $1 branch_location
  
  # Find the manifest files
  for loc in `find $1 -name "AndroidManifest.xml";`; do
  
    python3 ../../$python_parse_manifest get_sdk_version $loc

  done

}

function test_manifest_location {

#  cd $repo_dir
#  
#    output_loc="../../$version_root/$repo_dir/master"
#    attach_tag_head $output_loc master
#    manifest_locs=`find $output_loc -name "AndroidManifest.xml";`
#    python3 ../../$python_locate_manifests get_manifests $output_loc $manifest_locs
    
#    cd ../..
    
  output_loc="$version_root/$repo_dir/master"
  attach_tag_head $output_loc master
  manifest_locs=`find $output_loc -name "AndroidManifest.xml";`
  $python_runtime $python_locate_manifests get_manifests $output_loc $manifest_locs
}
	
### Make dirs if needed
	mkdir -p $gh_repos_dir
	mkdir -p $gh_log_dir
	touch $gh_log_file_clone

### Handle script
	if [ ! -z "$repo_name" ]; then 
		instantiate_repo
		echo "Cloned $repo_name."
	fi
  
#  if [ ! -z "$repo_dir" ]; then
#    get_releases
#    echo "Got releases under $repo_dir"
#  fi
  
  if [ ! -z "$tm_arg" ]; then
    test_manifest_location
  fi
  

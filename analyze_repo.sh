### This file contains scripts for analyzing a single git repository

### Usage
### 	analyze_repo [-a|--arg param]*
###       [-r|--repo repo_name] 
###         Specifies the name of the repo to perform the action on.
###         This will obtain the repo from github and then set the -d variable accordingly.
###       [-d|--directory cloned_repo_dir]
###         Specifies the directory to perform the action on.
###       [-p|--python]
###         Specifies the python 3.X runtime to use for executing python code.
###         Default is `python3`.

### Includes

## Change this include to switch out the database client
.   db_client/mysql_client.sh



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
    -p|--python)
    python_runtime="$2"
		shift # past argument
    shift # past argument
		;;
	esac
	done
	
### Functions
  
function repo_to_dir {
  # Converts a repo string to a valid directory name.
  # This is only done to reduce the number of directories created,
  # and possible issues arising from analyzing multiple directories
  # owned by the same user or organization
  # ex. "company/repository" -> "company-repository"
	c_d=${1//\//-}
	echo "$gh_repos_dir/$c_d"
}
	
function instantiate_repo {
  # Performs an initial clone on the repository.
  # For Example, the master branch of the repository where `-r` was
  # specified as `me/myRepo` would clone the master branch at 
  # github.com/me/myRepo.git into the local directory `$gh_repos_dir/me-myRepo/`
  #
  # Note: In order to avoid git from prompting for a username/password for 
  # repositories which require credentials, the clone command supplies a dummy 
  # usename and password of u:p.

	### Pulls the repository specified as a parameter
	gh_url="https://u:p@github.com/$repo_name.git"
	
	# Make the destination for the repo
	clone_dir=`repo_to_dir $repo_name`
	
	# Clone repsitory
	git clone --quiet $gh_url $clone_dir
  
  # Set the repo_dir to begin analysis
  repo_dir=$clone_dir
}

function checkout_branch_head {
  # Checks out the head of the specified branch.
  # This assumes that either a directory of an existing repository
  # has been specified with the `-d|--directory` switch, or that the 
  # current execution of the script cas set the $repo_dir variable. This 
  # variable is set in `instantiate_repo`.
  ### Parameters
  # $1 output_location
  # $2 tag to checkout the head of
    
  mkdir -p "$1"
  
  if [ -d "$repo_dir" ]; then
    cd $repo_dir
      
      # Check out the specified tag
      git checkout --quiet $2
      git --work-tree="../../$1" checkout --quiet HEAD -- .
    
      cd ../..
  fi
}

function checkout_commit {
  # Checks out a specific commit of the current repo.
  # This assumes that either a directory of an existing repository
  # has been specified with the `-d|--directory` switch, or that the 
  # current execution of the script cas set the $repo_dir variable. This 
  # variable is set in `instantiate_repo`.
  ### Parameters
  # $1 output_location
  # $2 commit to checkout
    
  mkdir -p "$1"
  
  if [ -d "$repo_dir" ]; then
    cd $repo_dir
      
      git --work-tree="../../$1" checkout --quiet $2
    
      cd ../..
  fi
}

function get_project_sdk_version {
  ### Parameters
  # $1 branch_location
  
  # Find the manifest files
  for loc in `find $1 -name "AndroidManifest.xml";`; do
  
    $python_runtime ../../$python_parse_manifest get_sdk_version $loc

  done

}

function get_commits_for_pertinent_files {
  # Gets the commit hashes for each commit that modified any of
  # the pertinent AndroidManifest or build.gradle files. For definitions
  # on what qualifies as pertinent, reference the assumptions.md file.
  # Duplicate commit hashes will be removed.
  #
  # The form of the commit hash will be `%ct~%H`, where %ct is the unix timestamp
  # of the commit hash, and %H is the commit hash.
  #
  # This assumes that either a directory of an existing repository
  # has been specified with the `-d|--directory` switch, or that the 
  # current execution of the script cas set the $repo_dir variable. This 
  # variable is set in `instantiate_repo`.
  ### Parameters
  # $1 output_location
  
  output_loc_master=$1/master
  checkout_branch_head $output_loc_master master
  manifest_locs=`find $output_loc_master -name "AndroidManifest.xml" -o -name "build.gradle";`
  pertinent_locations=`$python_runtime $python_locate_manifests get_manifests $output_loc_master $manifest_locs`
  
  # cd is needed because the git command references the current directory
  cd $repo_dir
    # Get each commit where one of the pertinent files was modified
    all_commits=""
    for loc in $pertinent_locations; do
      commits=`git log --pretty=format:"%ct~%H" --follow -- $loc`
      all_commits="$all_commits $commits"
    done
    cd ../..
  # Clean up master files
  rm -rf $output_loc_master
  # Sort commits by their UNIX timestamp (Also removes duplicates)
  echo $all_commits | tr " " "\n" | sort -nu
}

function get_commit_info {
  # gets the info for the given commit. This info is as follows:
  # A space separated list of
  # 1. the min API version for the Android Project
  # 2...n. the permissions contained in the Android Project
  ### Parameters
  # $1 the output location for this commit
  # $2 the commit sha
    
  # Get manifest content for this commit
  # TODO instead of finding these files each time, can we just use the locations from the master branch?
  this_commit_manifest_locs=`find $1 -name "AndroidManifest.xml" -o -name "build.gradle";`
  this_commit_manifest_display=`$python_runtime $python_locate_manifests display_manifests $1 $this_commit_manifest_locs`
  
  # Get Database call args
  api_and_sdk=`$python_runtime $python_locate_manifests get_sdk_perm $1 $this_commit_manifest_locs`
  echo $api_and_sdk
}

function analyze_repo {
  # Analyzes the given project for permissions and API version data for all
  # commits pertinent to the conditions specified in the assumptions.md file.
  
  # Get the output location for the current content
  output_loc="$version_root/$repo_dir"
  mkdir -p $output_loc
  # Get Pertinent commits
  commits=`get_commits_for_pertinent_files $output_loc`
  
  for commit in $commits; do
    # Clean the timestamp off the commit info, leaving just the hash
    commit_sha=`sed -e 's#.*~\(\)#\1#' <<< "$commit"`
    this_commit_output_loc=$output_loc/$commit_sha
    checkout_commit $this_commit_output_loc $commit_sha
    
    commit_info=`get_commit_info $this_commit_output_loc`
    echo $commit_info
    # Add to database
    insert_commit_info $commit_sha $commit_info
    # echo wasn't displaying newlines
    printf "$this_commit_manifest_display"
    rm -rf $this_commit_output_loc
  done
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
  
  analyze_repo
  
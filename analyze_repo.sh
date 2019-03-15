### This file contains scripts for analyzing a single git repository

### Usage
### 	analyze_repo 
###       [-r|--repo repo_name] 
###         Specifies the name of the repo to perform the action on.
###         This will obtain the repo from github and then set the -d variable accordingly.
###       [-d|--directory cloned_repo_dir]
###         Specifies the directory to perform the action on.
###       [-p|--python]
###         Specifies the python 3.X runtime to use for executing python code.
###         Default is `python3`.

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
    -p|--python)
    python_runtime="$2"
		shift # past argument
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
	
	# Clone repsitory
	git clone --quiet $gh_url $clone_dir
  
  # Set the repo_dir to begin analysis
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
    
  mkdir -p "$1"
  
  if [ -d "$repo_dir" ]; then
    cd $repo_dir
      
      # Check out the specified tag
      git checkout --quiet $2
      git --work-tree="../../$1" checkout --quiet HEAD -- .
    
      cd ../..
  fi
  
  echo "Checked out head of branch: $2"
}

function checkout_commit {
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

function get_branch_sdk_version {
  ### Parameters
  # $1 branch_location
  
  # Find the manifest files
  for loc in `find $1 -name "AndroidManifest.xml";`; do
  
    $python_runtime ../../$python_parse_manifest get_sdk_version $loc

  done

}

function test_manifest_location {

  output_loc="$version_root/$repo_dir"
  output_loc_master=$output_loc/master
  attach_tag_head $output_loc_master master
  manifest_locs=`find $output_loc_master -name "AndroidManifest.xml" -o -name "build.gradle";`
  pertinent_locations=`$python_runtime $python_locate_manifests get_manifests $output_loc_master $manifest_locs`
  # cd is needed because the cit command references the current directory
  cd $repo_dir
    # Get each commit where one of the pertinent files was modified
    all_commits=""
    for loc in $pertinent_locations; do
      commits=`git log --pretty=format:"%ct~%H" --follow -- $loc`
      all_commits="$all_commits $commits"
    done
    cd ../..
  # Sort commits by their UNIX timestamp (Also removes duplicates)
  sorted_commits=`echo $all_commits | tr " " "\n" | sort -nu`
  for commit in $sorted_commits; do
    # Get just the commit sha, now that we don't need timestamp for sorting
    commit_sha=`sed -e 's#.*~\(\)#\1#' <<< "$commit"`
    this_commit_output_loc=$output_loc/$commit_sha
    checkout_commit $this_commit_output_loc $commit_sha
    # Get manifest content for this commit
    # TODO instead of finding these files each time, can we just use the $pretinent_locations?
    this_commit_manifest_locs=`find $this_commit_output_loc -name "AndroidManifest.xml" -o -name "build.gradle";`
    this_commit_manifest_display=`$python_runtime $python_locate_manifests display_manifests $this_commit_output_loc $this_commit_manifest_locs`
  
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
  
#  if [ ! -z "$repo_dir" ]; then
#    get_releases
#    echo "Got releases under $repo_dir"
#  fi
  
  if [ ! -z "$tm_arg" ]; then
    test_manifest_location
  fi
  

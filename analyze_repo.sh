### This file contains scripts for analyzing a single git repository

### Usage
### 	`analyze_repo [-r|--repo repo_name] [-d|--directory cloned_repo_dir]`

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
	esac
	done

### Collected Repos root
	gh_repos_dir="./test_repos"
	
### Logs
	gh_log_dir="./gh_logs"
	gh_log_file_clone="$gh_log_dir/clone.txt"
	
function repo_to_dir {
	c_d=${1//\//-}
	echo "$gh_repos_dir/$c_d"
}
	
function instantiate_repo {
	### Pulls the repository specified as a parameter
	gh_url="https://github.com/$repo_name.git"
	
	# Make the destination for the repo
	clone_dir=`repo_to_dir $repo_name`
	
	# Clone repsitory and return duration of operation in seconds
	`git clone --quiet $gh_url $clone_dir`
}

function get_releases {
	### Gets the releases for the repo_name
	:
}
	
### Make dirs if needed
	mkdir -p $gh_repos_dir
	mkdir -p $gh_log_dir
	touch $gh_log_file_clone

### Handle script
	if [ -z "$repo_name" ] 
	then 
		:# No repo name supplied
	else
		`instantiate_repo`
		echo "Cloned $repo_name."
	fi

function test {
  for file in fdroid/fdroiddata/metadata/*.txt; do 
    gh_line=`grep "Source Code:https://github.com/" $file`
    gh_repo=$(sed 's|Source Code:https:\/\/github.com/||' <<< $gh_line)
    gh_repo=$(sed 's|(.git)?\s.*$||' <<< $gh_repo)
    echo $gh_repo
    
    if [ ! -z "$gh_repo" ]; then
      ./analyze_repo.sh -r $gh_repo --test-manifest >> out5.txt
    fi
  done
}

test
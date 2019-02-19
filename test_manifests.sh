function test {
  for file in fdroid/fdroiddata/srclibs/*; do 
    gh_line=`grep "github.com" $file`
    gh_repo=$(sed 's|Repo:https:\/\/github.com/||' <<< $gh_line)
    gh_repo=$(sed 's|.git||' <<< $gh_repo)
    if[ ! -z $gh_repo ]; then
      ./analyze_repo -r $gh_repo -tm asd
    fi
  done
}

test
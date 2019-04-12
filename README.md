# mobilepermissions_bc
This repository contains preliminary scripts that obtain public Android Github repositories, and analyze them 
for any relevant information located in their `AndroidManifest.xml` or `build.gradle` files.

## Installation

The script requires a linux operating system and python3 runtime to work

### Setup
// TODO

### Database Integration
// TODO

## Usage

`analyze_repo [-a|--arg param]* `

 `[-r|--repo repo_name]`

   Specifies the name of the repo to perform the action on.
   This will obtain the repo from github and then set the -d variable accordingly.

 `[-d|--directory cloned_repo_dir]`

   Specifies the directory to perform the action on.

 `[-p|--python]`

   Specifies the python 3.X runtime to use for executing python code.
   Default is `python3`.

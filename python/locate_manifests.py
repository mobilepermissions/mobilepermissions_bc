from manifest import Manifest
from head_manifest import HeadManifest
from gradle import GradleFile
import sys
import re

# Sometimes manifests will be included in directories that dont reflect the final implementation
# Here are some places I've identified as potentially problematic.
invalid_manifest_paths = r".*(/bin/|/test.?/|/androidTest/|/demo/).*"

def display_manifests(root, manifest_locs):
  # TODO read settings.gradle to look for included libraries?
  # This would be used to scan their values as well
  """
  Parses, merges, and displays all manifests and gradle files supplied in a human readable format
  This function is best used for debugging or validating parsing logic.
  """
  manifest_head = HeadManifest()
  print("Total files found: " + str(len(manifest_locs)) + "\n-----------------")
  for manifest_loc in manifest_locs:
    print(manifest_loc)
    if "AndroidManifest.xml" in manifest_loc:
      if not re.search(invalid_manifest_paths, manifest_loc):
        manifest_head, merged = manifest_head.merge(Manifest(root, manifest_loc))
    elif "build.gradle" in manifest_loc:
      manifest_head.add_gradle(GradleFile(root, manifest_loc))
  print("-----------------\n--Final Structure--\n" + str(manifest_head))
  return str(manifest_head.get_permissions()) + "\n"

def get_manifests(root, manifest_locs):
  """
  Gets a list of all manifests and gradle files that would be accounted for by the parsing logic
  
  returns a space-separated string of the manifest files.
  """
  manifest_head = HeadManifest()
  for manifest_loc in manifest_locs:
    if "AndroidManifest.xml" in manifest_loc:
      if not re.search(invalid_manifest_paths, manifest_loc):
        manifest_head, merged = manifest_head.merge(Manifest(root, manifest_loc))
    elif "build.gradle" in manifest_loc:
      manifest_head.add_gradle(GradleFile(root, manifest_loc))
  return str(manifest_head.get_pertinent_files())
  
def get_sdk_perm(root, manifest_locs):
  """
  Gets the SDK information and permissions from the given manifests.
  
  returns a space-separated string in the format of:
  [minSdkVersion] [permission]*
  """
  manifest_head = HeadManifest()
  for manifest_loc in manifest_locs:
    if "AndroidManifest.xml" in manifest_loc:
      if not re.search(invalid_manifest_paths, manifest_loc):
        manifest_head, merged = manifest_head.merge(Manifest(root, manifest_loc))
    elif "build.gradle" in manifest_loc:
      manifest_head.add_gradle(GradleFile(root, manifest_loc))
  return manifest_head.get_command_line_string()

if __name__ == "__main__":
  if len(sys.argv) >= 3:
    """
    Calling function from command line
    Usage
    python locate_manifests.py [function] [root_directory] [manifest/gradle location]*
    """
    if sys.argv[1] == 'display_manifests':
      print(display_manifests(sys.argv[2], sys.argv[3:]))
      print(" ")
    elif sys.argv[1] == 'get_manifests':
      print(get_manifests(sys.argv[2], sys.argv[3:]))
    elif sys.argv[1] == 'get_sdk_perm':
      print(get_sdk_perm(sys.argv[2], sys.argv[3:]))
    
    
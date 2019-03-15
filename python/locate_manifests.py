from manifest import Manifest
from head_manifest import HeadManifest
from gradle import GradleFile
import sys
import re

invalid_manifest_paths = r".*(/bin/|/test.?/|/androidTest/|/demo/).*"

def get_manifests(root, manifest_locs):
  # TODO read settings.gradle to look for included libraries?
  manifest_head = HeadManifest()
  print("Total files found: " + str(len(manifest_locs)) + "\n-----------------")
  for manifest_loc in manifest_locs:
    print(manifest_loc)
    if "AndroidManifest.xml" in manifest_loc:
      if not re.search(invalid_manifest_paths, manifest_loc):
        manifest_head, merged = manifest_head.merge(Manifest(manifest_loc))
    elif "build.gradle" in manifest_loc:
      manifest_head.add_gradle(GradleFile(manifest_loc))
  print("-----------------\n--Final Structure--\n" + str(manifest_head))
  return str(manifest_head.get_permissions()) + "\n"

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    print({
      'get_manifests': get_manifests(sys.argv[2], sys.argv[3:])
    }[sys.argv[1]])
from manifest import manifest
import sys
import re

invalid_manifest_paths = r".*(/bin/|/test.?/|/androidTest/|/demo/).*"

def get_manifests(root, manifest_locs):
  # TODO read settinds.gradle to look for included libraries?
  manifest_head = None
  print "Total manifests found: " + str(len(manifest_locs)) + "\n-----------------"
  for manifest_loc in manifest_locs:
    print manifest_loc
    if not re.search(invalid_manifest_paths, manifest_loc):
      manifest_head = manifest(manifest_loc).merge(manifest_head)
  print "-----------------\n--Final Structure--\n" + str(manifest_head)
  return str(manifest_head is not None) + "\n"

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    print {
      'get_manifests': get_manifests(sys.argv[2], sys.argv[3:])
    }[sys.argv[1]]
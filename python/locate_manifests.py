from manifest import manifest
import sys

def get_manifests(root, manifest_locs):
  manifest_head = None
  for manifest_loc in manifest_locs:
    path_start = manifest_loc.find(root) + len(root)
    manifest_head = manifest(manifest_loc[path_start:]).merge(manifest_head)
  return manifest_head is not None

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    print {
      'get_manifests': get_manifests(sys.argv[2], sys.argv[3:])
    }[sys.argv[1]]
from enum import IntEnum
import re

class manifest:

  primary_child = None
  # Lazily initiated in get_manifest_level()
  manifest_level = None
  
  min_sdk_version = 1
  target_sdk_version = 1
  
  permissions = []
  

  def __init__(self, location):
    self.location = location
    
    # Replace all "../" operations and the manifest filename
    trimmed_location = re.sub(r"([.]{1,2}[/]{1,2}|AndroidManifest.xml)", "", location)
    if len(trimmed_location) > 0 and trimmed_location[0] == '/':
      trimmed_location = trimmed_location[1, len(trimmed_location-1)]
      
    self.path = trimmed_location
    
  
  def __str__(self):
    return self.nested_str(0)
    
  def nested_str(self, depth):
    ret = "\t"*depth + "-" + self.location + "\n" 
    if self.primary_child is not None:
      ret += self.primary_child.nested_str(depth+1)
    return ret
    
    
  def get_manifest_level(self):
    if self.manifest_level == None:
      
      if self.path == "":
        self.manifest_level = manifest_level.library
      elif re.search(r"(android/|mobile/)(src/)?(main/)?$", self.path):
        self.manifest_level = manifest_level.main
      elif re.search(r"release/$", self.path):
        self.manifest_level = manifest_level.build_variant
      else:
        self.manifest_level = manifest_level.unknown
    
    return self.manifest_level
    
    
  def merge(self, other_manifest):
    # Determine if any either of the manifests is a sub-manifest
    # of the other one
    
    # If this manifest is a child of the other manifest
    if self.path.find(other_manifest.path) != -1:
      return merge_parent_child_manifest(other_manifest, self)
      
    if other_manifest.path.find(self.path) != -1:
      return merge_parent_child_manifest(self, other_manifest)
      
    ## If neither is a substring, then at least one of them must be 
    ## of an incorrect build variant or main type.
    
    # In this case, we have two unclassifiable manifest files that are
    # un-related by our definitions
    if self.get_manifest_level() == -1 and other_manifest.get_manifest_level() == -1:
      return None
      
    # If the two manifests are not associated but are both valid,
    # then return the manifest with that has a lower manifest level
    # This is done because in the case of:
    # Valid build variant, and valid main --> discard build variant to preserve main
    #     ex. project contains a main manifest for android build
    #         and also contains a release manifest for wearable build
    if self.get_manifest_level() < other_manifest.get_manifest_level():
      return self
    return other
    
  
def merge_parent_child_manifest(parent, child):
  new_child = child
  # Determine if this manifest is a child of child of the parent manifest
  if parent.primary_child is not None:
    new_child = parent.primary_child.merge(child)
  # Set Child
  parent.primary_child = new_child
  return parent
    
    
    
class manifest_level(IntEnum):
  library = 1
  main = 2
  build_variant = 3
  unknown = 404
  
  
  
if __name__ == "__main__":
  man1 = manifest("../../AndroidManifest.xml")
  man2 = manifest("../../mobile/src/main/AndroidManifest.xml")
  man3 = manifest("../../mobile/src/main/release/AndroidManifest.xml")
  man4 = manifest("../../mobile/src/main/androidTest/AndroidManifest.xml")
  
  print man1.merge(man2).merge(man3).merge(man4)
  print man4
  
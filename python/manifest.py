from enum import IntEnum
import re

class manifest:

  

  def __init__(self, location):
    self.location = location
    
    self.primary_child = None
    # Lazily initiated in get_manifest_level()
    self.manifest_level = None
    
    self.min_sdk_version = 1
    self.target_sdk_version = 1
    
    self.permissions = []
  
    
    # Replace all "../" operations and the manifest filename
    trimmed_location = re.sub(r"([.]{1,2}[/]{1,2}|AndroidManifest.xml)", "", location)
    # Then, replace the initial "/" char if needed
    trimmed_location = re.sub(r"^/", "", trimmed_location)
    
    self.path = trimmed_location
    
  
  def __str__(self):
    return self.nested_str(0)
    
    
  def nested_str(self, depth):
    # Recursive printing of manifest nesting
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
    
    
  def get_min_sdk_version(self):
    if self.primary_child is None:
      return self.min_sdk_version
    return max(self.min_sdk_version, self.primary_child.get_min_sdk_version())
    
    
  def get_target_sdk_version(self):
    if self.primary_child is None:
      return self.target_sdk_version
    return max(self.min_sdk_version, self.primary_child.get_target_sdk_version())
    
  
  def get_permissions(self):
    # TODO account for duplicate permissions?
    if self.primary_child is None:
      return self.permissions
    return self.permissions + self.primary_child.get_permissions()
    
    
  def merge(self, other_manifest):
    # Determine if any either of the manifests is a sub-manifest
    # of the other one
    
    # If this manifest is a child of the other manifest
    if self.path.find(other_manifest.path) != -1:
      return manifest.merge_parent_child_manifest(other_manifest, self)
     
    # If the other manifest is a child of this manifest
    if other_manifest.path.find(self.path) != -1:
      return manifest.merge_parent_child_manifest(self, other_manifest)
      
    ## If neither is a child, then at least one of them must be 
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
    return other_manifest
    
  
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
  man1.permissions += [1, 2]
  man1.min_sdk_version = 15
  man2 = manifest("../../mobile/src/main/AndroidManifest.xml")
  man2.permissions += [4]
  man3 = manifest("../../mobile/src/main/release/AndroidManifest.xml")
  man3.permissions += [10]
  man3.min_sdk_version = 23
  man3.target_sdk_version = 28
  man4 = manifest("../../mobile/src/main/androidTest/AndroidManifest.xml")
  man4.permissions += [1, 5]
  man5 = manifest("../../glass/src/main/release/AndroidManifest.xml")
  man5.permissions += [11]
  man6 = manifest("../../wear/src/main/release/AndroidManifest.xml")
  man7 = manifest("../../wear/src/main/AndroidManifest.xml")
  
  man = man1.merge(man4).merge(man2).merge(man7).merge(man5).merge(man6).merge(man3)
  print man
  print man.get_permissions()
  print man.get_min_sdk_version()
  print man.get_target_sdk_version()
  
  
from enum import Enum
import re

class manifest:

  children = []
  manifest_level = None
  

  def __init__(self, location):
    self.location = location
    
    # Replace all "../" operations and the manifest filename
    trimmed_location = re.sub(r"([.]{1,2}[/]{1,2}|AndroidManifest.xml)", "", location)
    if len(trimmed_location) > 0 and trimmed_location[0] == '/':
      trimmed_location = trimmed_location[1, len(trimmed_location-1)]
      
    self.path = trimmed_location
    
    print self.path
    
    
  def get_manifest_level(self):
    if self.manifest_level == None:
      
      if self.path == "":
        self.manifest_level = manifest_level.library
      elif re.search(r"(android/|mobile/)(src/)?(main/)?$", self.path) != -1:
        self.manifest_level = manifest_level.main
      elif re.search(r"release/$", self.path) != -1:
        self.manifest_level = manifest_level.build_variant
      else:
        self.manifest_level = manifest_level.unknown
    
    return self.manifest_level
    
    
  def merge_manifest(self, other_manifest):
    if self.path.find(other_manifest.path) != -1:
      self.children.append(other_manifest)
      return self
    if other_manifest.path.find(self.path) != -1:
      other_manifest.children.append(self)
      return other_manifest
    ## If neither is a substring, then one of them must be 
    ## of an incorrect build variant or main type, so:
    ##    1. Search to see if the manifest is under a known
    ##        directory for android builds
    
    
    
    
    
    
class manifest_level(Enum):
  library = 1
  main = 2
  build_variant = 3
  unknown = -1
  
  
if __name__ == "__main__":
  print manifest("../../asd123/AndroidManifest.xml").get_manifest_level()
  print manifest("../../android/AndroidManifest.xml").get_manifest_level()
  print manifest("../../mobile/AndroidManifest.xml").get_manifest_level()
  print manifest("../../mobile/src/main/AndroidManifest.xml").get_manifest_level()
  print manifest("../../AndroidManifest.xml").get_manifest_level()
  print manifest("../../mobile/src/main/release/AndroidManifest.xml").get_manifest_level()
  print manifest("../../mobile/src/main/androidTest/AndroidManifest.xml").get_manifest_level()
# -*- coding: utf-8 -*-

from manifest import Manifest, manifest_level
from gradle import GradleFile

class HeadManifest(Manifest):

  def __init__(self):
    Manifest.__init__(self, "HEAD")
    self.head_children = []
    self.gradle_files = []
    self.manifest_level = manifest_level.head
  
  def __str__(self):
    ret = "HEAD (minSDK=" + str(self.get_min_sdk_version()) + ", targetSDK="  + str(self.get_target_sdk_version()) + ", permCount=" + str(len(self.get_permissions())) + ")" 
    cur_child = 0
    for child in self.head_children:
      cur_child = cur_child + 1
      ret += "\n" + child.nested_str(0, cur_child == len(self.head_children))
    for gradle_file in self.gradle_files:
      ret += '\n' + str(gradle_file)
    return ret

  def merge(self, other_manifest):
    if other_manifest.get_manifest_level() != manifest_level.unknown:
      # attempt to merge into each of the children of the head
      for child in self.head_children:
        merged_child, merged = child.merge(other_manifest)
        # If it was successfully merged, dont add it to children
        if merged:
          # If it was merged with a manifest which was its parent
          if merged_child != child:
            # replace its reference with its parent
            self.head_children.remove(child)
            self.head_children.append(merged_child)
          return self, True
      self.head_children.append(other_manifest)
      return self, True
    # print("Throwing out manifest: " + str(other_manifest.path))
    return self, False
    
  def get_min_sdk_version(self):
    min_sdk_version = 1
    for child in self.head_children:
      child_sdk = child.get_min_sdk_version()
      if child_sdk is not None:
        min_sdk_version = max(min_sdk_version, child_sdk)
    for gradle_file in self.gradle_files:
      gradle_sdk = gradle_file.get_min_sdk()
      min_sdk_version = max(min_sdk_version, gradle_sdk)
    return min_sdk_version
    
  def get_target_sdk_version(self):
    target_sdk_version = 1
    for child in self.head_children:
      child_sdk = child.get_target_sdk_version()
      if child_sdk is not None:
        target_sdk_version = max(target_sdk_version, child_sdk)
    for gradle_file in self.gradle_files:
      gradle_sdk = gradle_file.get_target_sdk()
      target_sdk_version = max(target_sdk_version, gradle_sdk)
    return target_sdk_version
    
  def get_permissions(self):
    permissions = []
    for child in self.head_children:
      permissions += child.get_permissions()
    return set(permissions)
    
  def add_gradle(self, gradle):
    self.gradle_files.append(gradle)
    
  
  
if __name__ == "__main__":
  man0 = HeadManifest()
  man1 = Manifest("AndroidManifest.xml")
  man2 = Manifest("mobile/src/main/AndroidManifest.xml")
  man3 = Manifest("mobile/src/main/release/AndroidManifest.xml")
  man4 = Manifest("mobile/src/main/androidTest/AndroidManifest.xml")
  man5 = Manifest("glass/src/main/release/AndroidManifest.xml")
  man6 = Manifest("wear/src/main/release/AndroidManifest.xml")
  man7 = Manifest("wear/src/main/AndroidManifest.xml")
  man8 = Manifest("externalLibrary/AndroidManifest.xml")
  man9 = Manifest("externalLibrary/src/main/AndroidManifest.xml")
  
  
  man, x = man0.merge(man1)
  man, x = man.merge(man4)
  man, x = man.merge(man2)
  man, x = man.merge(man7)
  man, x = man.merge(man5)
  man, x = man.merge(man6)
  man, x = man.merge(man3)
  man, x = man.merge(man8)
  man, x = man.merge(man9)
  print(man)
  

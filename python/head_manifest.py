# -*- coding: utf-8 -*-

from manifest import Manifest, manifest_level

class HeadManifest(Manifest):

  def __init__(self):
    #super(type(HeadManifest), self).__init__()
    Manifest.__init__(self, "HEAD")
    self.head_children = []
    self.manifest_level = manifest_level.head
  
  def __str__(self):
    ret = "HEAD"
    cur_child = 0
    for child in self.head_children:
      cur_child = cur_child + 1
      ret += "\n" + child.nested_str(0, cur_child == len(self.head_children))
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
    
  
  
if __name__ == "__main__":
  man0 = HeadManifest()
  man1 = Manifest("app/AndroidManifest.xml")
  man1.permissions += [1, 2]
  man1.min_sdk_version = 15
  man2 = Manifest("app/mobile/src/main/AndroidManifest.xml")
  man2.permissions += [4]
  man3 = Manifest("app/mobile/src/main/release/AndroidManifest.xml")
  man3.permissions += [10]
  man3.min_sdk_version = 23
  man3.target_sdk_version = 28
  man4 = Manifest("app/mobile/src/main/androidTest/AndroidManifest.xml")
  man4.permissions += [1, 5]
  man5 = Manifest("app/glass/src/main/release/AndroidManifest.xml")
  man5.permissions += [11]
  man6 = Manifest("app/wear/src/main/release/AndroidManifest.xml")
  man7 = Manifest("app/wear/src/main/AndroidManifest.xml")
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
  

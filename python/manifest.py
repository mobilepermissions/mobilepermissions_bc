# -*- coding: utf-8 -*-

from enum import IntEnum
from parse_manifest import ManifestParser
import re

class Manifest():
  """
  A Python wrapper for a `AndroidManifest.xml` file, which maintains information
  about the file, and organizes it relative to its children.
  
  See Android documentation (https://developer.android.com/studio/build/manifest-merge)
  for child merging logic.
  """

  def __init__(self, root, location):
    self.location = re.sub(re.escape(root) + r"/","",location)
    
    self.primary_child = None
    # Lazily initiated in get_manifest_level()
    self.manifest_level = None
    
    self.parser = ManifestParser(location)
    
    # Replace all "../" operations and the manifest filename
    trimmed_location = re.sub(r"([.]{1,2}[/]{1,2}|AndroidManifest.xml)", "", self.location)
    # Then, replace the initial "/" char if needed
    trimmed_location = re.sub(r"^/", "", trimmed_location)
    
    self.path = trimmed_location
    
  
  def __str__(self):
    return self.nested_str(0)
    
    
  def nested_str(self, depth, final = False):
    """
    Intermitten operation for converting the manifest listing to a String.
    
    This logic is primarily called from head_manifest.py and is used to format
    the entire manifest heirarchy in a familiar format
    
    This function does not relate to database entries, and is intended only for
    use in debugging & displaying human readable represetations of merging logic.
    """
    # Determine what characters should be pre-pended for display purposes
    tree_char = '└'
    pre_pend_char = '│'
    if depth == 0 and not final:
      tree_char = '├'
    if final:
      pre_pend_char = ''
    # Recursive printing of manifest nesting
    ret = "    "*depth + tree_char + "── " + self.location + " (minSDK=" + str(self.parser.get_min_sdk_version()) + ", targetSDK=" + str(self.parser.get_target_sdk_version()) + ", permCount=" + str(len(self.parser.get_permissions())) + ")"
    if self.primary_child is not None:
      ret += "\n" + pre_pend_char + self.primary_child.nested_str(depth+1, final)
    return ret
    
    
  def get_manifest_level(self):
    """
    Uses the manifest directory location to determine what level of Manifest
    the file is. See Android documentation (https://developer.android.com/studio/build/manifest-merge)
    for details on the merging structure.
    
    Worlks as a lazy getter, and successive calls will not repeat the logic.
    """
    if self.manifest_level == None:
    
      if re.search(r"(glass/|wear/|androidTest/|test/)", self.path):
        self.manifest_level = manifest_level.unknown
      elif re.search(r"release/$", self.path):
        self.manifest_level = manifest_level.build_variant
      elif re.search(r".*/.*(src/main)?/$", self.path):
        self.manifest_level = manifest_level.main
      elif self.path.count('/') <= 1:
        self.manifest_level = manifest_level.library
      else:
        self.manifest_level = manifest_level.unknown
    
    return self.manifest_level
    
    
  def get_min_sdk_version(self):
    """
    Uses the parser to get this file's value for the field, and then
    determines if there is a child with a value which will take priority.
    
    For information on merging logic, reference Android documentation here
    (https://developer.android.com/studio/build/manifest-merge)
    """
    self_min_sdk = self.parser.get_min_sdk_version()
    if self.primary_child is None:
      return self_min_sdk
    child_min_sdk = self.primary_child.get_min_sdk_version()
    
    # If either of the values is None, return the other.
    # It's okay if None is returned here
    if self_min_sdk == None:
      return child_min_sdk
    if child_min_sdk == None:
      return self_min_sdk
    # Otherwise return the max of the two
    return max(child_min_sdk, self_min_sdk)
    
    
  def get_target_sdk_version(self):
    """
    Uses the parser to get this file's value for the field, and then
    determines if there is a child with a value which will take priority.
    
    For information on merging logic, reference Android documentation here:
    (https://developer.android.com/studio/build/manifest-merge)
    """
    self_target_sdk = self.parser.get_target_sdk_version()
    if self.primary_child is None:
      return self_target_sdk
    child_target_sdk = self.primary_child.get_target_sdk_version()
    
    # If either of the values is None, return the other.
    # It's okay if None is returned here
    if self_target_sdk == None:
      return child_target_sdk
    if child_target_sdk == None:
      return self_target_sdk
    # Otherwise return the max of the two
    return max(child_target_sdk, self_target_sdk)
    
  
  def get_permissions(self):
    """
    Uses the parser to get this file's value for the field, and then
    merges the values with the manifest's children.
    
    For information on merging logic, reference Android documentation here:
    (https://developer.android.com/studio/build/manifest-merge)
    """
    # TODO account for duplicate permissions?
    self_permissions = self.parser.get_permissions()
    if self.primary_child is None:
      return self_permissions
    return self_permissions + self.primary_child.get_permissions()
    
    
  def merge(self, other_manifest):
    """
    Attempts to merge the manifest with another manifest.
    
    This function should not be called when attempting to merge a
    non-head manifest with a head_manifest. Instead, call head_manifest.merge()
    and pass this manifest object as a parameter.
    
    For information on manifest merging logic, reference the Android documentation here:
    (https://developer.android.com/studio/build/manifest-merge)
    """
    if other_manifest is None:
      return self, False
    # Determine if any either of the manifests is a sub-manifest
    # of the other one
    
    # Case: App Library Manifest located in parent directory of library
    if self.get_manifest_level() == manifest_level.library \
        and other_manifest.get_manifest_level == manifest_level.library:
      return self, False
    
    # If this manifest is a child of the other manifest
    # And this isn't the head
    if (self.path.find(other_manifest.path) == 0 \
        or other_manifest.get_manifest_level() == manifest_level.head) \
        and self.get_manifest_level() != manifest_level.head:
      return Manifest.merge_parent_child_manifest(other_manifest, self)
     
    # If the other manifest is a child of this manifest
    if other_manifest.path.find(self.path) == 0 \
        or self.get_manifest_level() == manifest_level.head:
      return Manifest.merge_parent_child_manifest(self, other_manifest)
      
    ## If neither is a child, then at least one of them must be 
    ## of an incorrect build variant or main type.
    
    # In this case, we have two unclassifiable manifest files that are
    # un-related by our definitions
    if self.get_manifest_level() == -1 and other_manifest.get_manifest_level() == -1:
      return None, False
      
    # If the two manifests are not associated but are both valid,
    # then return the manifest with that has a lower manifest level
    # This is done because in the case of:
    # Valid build variant, and valid main --> discard build variant to preserve main
    #     ex. project contains a main manifest for android build
    #         and also contains a release manifest for wearable build
    if self.get_manifest_level() < other_manifest.get_manifest_level():
      return self, False
    return other_manifest, False
    
  
  def merge_parent_child_manifest(parent, child):
    """
    Tries to merge the `child` manifest file into the `parent`, but first tries
    to merge the `child` into the first child of the `parent`.
    
    Diagram to hopefully clear up confusion:
    
    Case: parent doesn't have child
    
      Parent                   Parent
                     -->         |---- NewChild
                   
    Case: parent does have child & `child` is a child of `parent.child`
    
      Parent                 Parent
        |---- Child  -->         |---- Child
                                         |---- NewChild
                                         
    Case: parent does have a child but `child` is not a child of `parent.child`
    
      Parent                 Parent
        |---- Child  -->         |---- NewChild

    Recursion occurs here in the case of merging with the parent's child. Though
    there is no reasonable use case for this given the Android merging logic here:
    (https://developer.android.com/studio/build/manifest-merge)
    """
    new_child = child
    merged = True
    # Determine if this manifest is a child of child of the parent manifest
    if parent.primary_child is not None:
      new_child, merged = parent.primary_child.merge(child)
    # Set Child
    parent.primary_child = new_child
    return parent, merged
    
  def get_self_and_children_paths(self):
    """
    Gets the paths of this manifest and all children recursively
    returns a list of the manifest paths
    """
    if self.primary_child is not None:
      child_locs = self.primary_child.get_self_and_children_paths()
      if child_locs is not None:
        return [self.location] + child_locs
    return [self.location]
    
    
    
class manifest_level(IntEnum):
  head = 0
  library = 1
  main = 2
  build_variant = 3
  unknown = 404
  

  
  
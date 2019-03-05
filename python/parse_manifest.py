import sys
import xml.etree.ElementTree as ET

min_sdk_version_attribute = "{http://schemas.android.com/apk/res/android}minSdkVersion"
target_sdk_version_attribute = "{http://schemas.android.com/apk/res/android}targetSdkVersion"
permission_name_attribute = "{http://schemas.android.com/apk/res/android}name"

class ManifestParser:

  def __init__(self, loc):
    self.manifest_location = loc
    # Lazily initiated vars
    self.manifest_contents = None
    # SDK Version
    self.min_sdk_version = -1
    self.target_sdk_version = -1
    # Permissions
    self.permissions = None

  def get_min_sdk_version(self):
    # Lazy getter for min_sdk_version
    
    # Try to set from parser, default to 1 otherwise
    if self.min_sdk_version == -1:
      try:
        self.min_sdk_version = int(self.parse_manifest_for_sdk_version(min_sdk_version_attribute))
      except (KeyError, ValueError, TypeError) as err:
        self.min_sdk_version = None
      
    return self.min_sdk_version

  def get_target_sdk_version(self):
    # Lazy getter for min_sdk_version
    # Try to set from parser, default to 1 otherwise
    if self.target_sdk_version == -1:
      try:
        self.target_sdk_version = int(self.parse_manifest_for_sdk_version(target_sdk_version_attribute))
      except (KeyError, ValueError, TypeError) as err:
        self.target_sdk_version = None
      
    return self.target_sdk_version
    
  def parse_manifest_for_sdk_version(self, version_type):
    # Parse manifest file
    if self.manifest_contents is None:
      self.manifest_contents = ET.parse(open(self.manifest_location, 'r'))
    root = self.manifest_contents.getroot()
    for uses_sdk in root.findall("./uses-sdk"):
      return uses_sdk.attrib[version_type]
      
  def get_permissions(self):
    if self.permissions is None:
      self.permissions = []
      if self.manifest_contents == None:
        self.manifest_contents = ET.parse(open(self.manifest_location, 'r'))
      root = self.manifest_contents.getroot()
      for permission in (root.findall("./uses-permission") + root.findall("./uses-permission-sdk-23")):
        permission_name = permission.attrib[permission_name_attribute]
        if permission_name is not None:
          self.permissions.append(permission_name) 
    return self.permissions

"""
if __name__ == "__main__":
  if len(sys.argv) >= 2:
    print({
      'get_sdk_version': get_sdk_version(sys.argv[2])
    }[sys.argv[1]])
    """

import sys
import xml.etree.ElementTree as ET

min_sdk_version_attribute = "{http://schemas.android.com/apk/res/android}minSdkVersion"
target_sdk_version_attribute = "{http://schemas.android.com/apk/res/android}targetSdkVersion"

class ManifestParser:

  def __init__(self, loc):
    self.manifest_location = loc
    # Lazily initiated vars
    self.min_sdk_version = -1
    self.target_sdk_version = -1
    self.manifest_contents = None

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
    if self.manifest_contents == None:
      self.manifest_contents = ET.parse(open(self.manifest_location, 'r'))
    root = self.manifest_contents.getroot()
    for uses_sdk in root.findall("./uses-sdk"):
      return uses_sdk.attrib[version_type]

"""
if __name__ == "__main__":
  if len(sys.argv) >= 2:
    print({
      'get_sdk_version': get_sdk_version(sys.argv[2])
    }[sys.argv[1]])
    """

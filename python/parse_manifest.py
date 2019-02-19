import sys
import xml.etree.ElementTree as ET

min_sdk_version_attribute = "{http://schemas.android.com/apk/res/android}minSdkVersion"
target_sdk_version_attribute = "{http://schemas.android.com/apk/res/android}targetSdkVersion"

def get_sdk_version(location):
  manifest_contents = ET.parse(open(location, 'r'))
  root = manifest_contents.getroot()
  for uses_sdk in root.findall("./uses-sdk"):
    return location + ": " + uses_sdk.attrib[min_sdk_version_attribute]

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    print {
      'get_sdk_version': get_sdk_version(sys.argv[2])
    }[sys.argv[1]]
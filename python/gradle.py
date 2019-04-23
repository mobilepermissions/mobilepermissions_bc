import re


class GradleFile():
  """
  Python wrapper for a `build.gradle` file
  """

  def __init__(self, root, location):
    self.location = re.sub(re.escape(root) + r"/","",location)
    
    self.parser = GradleParser(location)
    
  def __str__(self):
    return "%s (minSdk=%d, targetSdk=%d)" % (self.location, self.get_min_sdk(), self.get_target_sdk())
    
  def get_min_sdk(self):
    return self.parser.get_min_sdk()
    
  def get_target_sdk(self):
    return self.parser.get_target_sdk()
    

class GradleParser():
  """
  Handling logic to be performed on a `build.gradle` file
  """
  
  def __init__(self, location):
    self.location = location
    
    # Lazily initiated vars
    self.gradle_contents = None
    self.min_sdk = -1
    self.target_sdk = -1
    
  def get_min_sdk(self):
    """
    Uses regex to find the minSdkVersion located in the `build.gradle` file
    The file should contain the string `minSdkVersion ([1-9]*)`
    
    This functions as a lazy getter for the min_sdk, as the parsing logic is only run once
    and successive calls to this function will return the stored value.
    
    If no value is found, then return -1 (this does not set the value lazily and 
    the file will be parsed in successive calls to this function in the future.
    """
    if self.min_sdk == -1:
      self.min_sdk = 1
      self.load_file()
      match = re.search(r'minSdkVersion ([1-9]*)', self.gradle_contents)
      if match is not None:
        try:
          self.min_sdk = int(match.group(1))
        except (TypeError, ValueError) as e:
          # Found a non-integer value for the minSdkVersion
          pass
      
    return self.min_sdk
  
  def get_target_sdk(self):
    """
    Uses regex to find the targetSdkVersion located in the `build.gradle` file
    The file should contain the string `targetSdkVersion ([1-9]*)`
    
    This functions as a lazy getter for the target_sdk, as the parsing logic is only run once
    and successive calls to this function will return the stored value
    
    If no value is found, then return -1 (this does not set the value lazily and 
    the file will be parsed in successive calls to this function in the future.
    """
    if self.target_sdk == -1:
      self.target_sdk = 1
      self.load_file()
      match = re.search(r'targetSdkVersion ([1-9]*)', self.gradle_contents)
      if match is not None:
        try:
          self.target_sdk = int(match.group(1))
        except (TypeError, ValueError) as e:
          pass
    
    return self.target_sdk
    
  def load_file(self):
    """
    Loads a file into the parser, storing its contents in memory
    
    Successive calls of this function will not re-parse the file or allocate additional memory
    """
    if self.gradle_contents is None:
        with open(self.location, 'r') as content_file:
          self.gradle_contents = content_file.read()
    
  
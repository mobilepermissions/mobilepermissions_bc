import re


class GradleFile():

  def __init__(self, location):
    self.location = re.sub(r".*/master/","",location)
    
    self.parser = GradleParser(location)
    
  def __str__(self):
    return "%s (minSdk=%d, targetSdk=%d)" % (self.location, self.get_min_sdk(), self.get_target_sdk())
    
  def get_min_sdk(self):
    return self.parser.get_min_sdk()
    
  def get_target_sdk(self):
    return self.parser.get_target_sdk()
    

class GradleParser():

  def __init__(self, location):
    self.location = location
    
    # Lazily initiated vars
    self.gradle_contents = None
    self.min_sdk = -1
    self.target_sdk = -1
    
  def get_min_sdk(self):
    if self.min_sdk == -1:
      self.min_sdk = 1
      self.load_file()
      match = re.search(r'minSdkVersion ([1-9]*)', self.gradle_contents)
      if match is not None:
        try:
          self.min_sdk = int(match.group(1))
        except (TypeError, ValueError) as e:
          pass
      
    return self.min_sdk
  
  def get_target_sdk(self):
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
    if self.gradle_contents is None:
        with open(self.location, 'r') as content_file:
          self.gradle_contents = content_file.read()
    
  
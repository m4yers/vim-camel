import sys
import os


def SetupEnv(root):
  sys.path.insert( 0, os.path.join( root, 'python', 'camel' ) )

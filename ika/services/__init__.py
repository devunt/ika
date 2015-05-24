import glob
import os


modulenames = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
modulenames = map(lambda x: os.path.basename(x)[:-3], modulenames)
modulenames = [f for f in modulenames if f != '__init__']

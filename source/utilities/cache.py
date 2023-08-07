# import os
# from joblib import Memory
# import joblib

# memory = Memory('./cachedir', verbose=0)

from joblib import Memory

memory = Memory('./cachedir', verbose=0)
# cachethis = memory.cache
cachethis = lambda f: f

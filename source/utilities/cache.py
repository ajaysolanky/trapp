from joblib import Memory

memory = Memory('./cachedir', verbose=0)
cachethis = memory.cache

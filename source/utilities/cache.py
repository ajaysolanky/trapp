# import os
# from joblib import Memory
# import joblib

# memory = Memory('./cachedir', verbose=0)

from joblib import Memory

memory = Memory('./cachedir', verbose=0)
cachethis = memory.cache

# def cachethis(func):

#     @memory.cache
#     def wrapper(*args, **kwargs):
#         value = wrapper.cache.get(args, None)
#         if value is None:
#             print("Cache miss") 
#             value = func(*args, **kwargs)
#             wrapper.cache[args] = value
#         else:
#             print("Cache hit")
#         return value

#     wrapper.cache = {}

#     return wrapper
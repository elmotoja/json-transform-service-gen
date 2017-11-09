import os

# print os.listdir('./')

for thing in os.listdir('./'):
    if 'service' in thing:
        os.remove(thing)


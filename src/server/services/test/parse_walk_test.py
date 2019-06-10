import os
import json

def parse_walk(walk, path):
    dir_tup = [t for t in walk if t[0] == path][0]
    walk.remove(dir_tup)
    tree = []
    
    for dir_name in dir_tup[1]:
        tree.append((dir_name, parse_walk(walk, os.path.join(path, dir_name))))
    for file_name in dir_tup[2]:
        tree.append(file_name)
        
    return tree
    
p = '/home/robin/college/pse/cte/src/server/services'
w = os.walk(p)
print(json.dumps(parse_walk(list(w), p)))
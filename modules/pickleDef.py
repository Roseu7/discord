import pickle
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
links_p = os.path.join(current_dir, '..', 'data', 'links.pickle')
osu_p = os.path.join(current_dir, '..', 'data', 'osu.pickle')
name_p = os.path.join(current_dir, '..', 'data', 'name.pickle')
other_p = os.path.join(current_dir, '..', 'data', 'data.pickle')

def pickle_dump(obj, path):
    with open(path, mode="wb") as f:
        pickle.dump(obj, f)

def pickle_load(path, default=None):
    try:
        with open(path, mode="rb") as f:
            return pickle.load(f)
    except (EOFError, FileNotFoundError):
        if default is not None:
            with open(path, mode="wb") as f:
                pickle.dump(default, f)
            return default
        else:
            return []

def link_dump(link_list):
    pickle_dump(link_list, links_p)

def link_load(default=None):
    link_list = pickle_load(links_p, default=default)
    return link_list

def osu_dump(osu_list):
    pickle_dump(osu_list, osu_p)

def osu_load(default=None):
    osu_dict = pickle_load(osu_p, default=default)
    return osu_dict

def name_dump(name_dict):
    pickle_dump(name_dict, name_p)

def name_load(default=None):
    name_dict = pickle_load(name_p, default=default)
    return name_dict

def other_dump(other_dict):
    pickle_dump(other_dict, other_p)

def other_load(default=None):
    other_dict = pickle_load(other_p, default=default)
    return other_dict
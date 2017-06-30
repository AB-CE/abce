from multiprocessing.managers import BaseManager
from collections import defaultdict
from copy import deepcopy


class Postbox:
    def __init__(self):
        self.boxes = defaultdict(dict)

    def receive(self, group, id):
        return self.boxes[group][id]

    def clear(self, group):
        self.boxes[group] = {}

    def copy(self, group_names):
        return {group: deepcopy(self.boxes[group]) for group in group_names}

    def send(self, group, id, message):
        try:
            self.boxes[group][id].append(message)
        except KeyError:
            self.boxes[group][id] = [message]


class PostboxManager(BaseManager):
    pass

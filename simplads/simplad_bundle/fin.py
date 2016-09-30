from .simplad_bundle import SimpladBundle
from .lift import lift

class fin(object):
    def __init__(self, first):
        self.first = first
        self.sm = SimpladBundle()

    def add_error(self):
        self.sm.add_error()
        return self

    def pipe(self, *args):
        return SimpladBundle().unit(self.first).pipe([i for i in args])

from django.utils.datastructures import SortedDict

class Digraph(SortedDict):
    def __init__(self, roots=None):
        if roots:
            map(self.arc, roots)

    def __missing__(self, key):
        val = []
        self[key] = val
        return val

    def arc(self, key, *values):
        self[key] = []
        for value in values:
            self[key].append(value)

            # ensure there's a key for this dependency
            if not value in self:
                self[value] = []

    def leafs(self):
        """
        Leafs have no children, they don't depend on any other objects
        """
        for node, deplist in self.items():
            if not deplist or len(deplist) < 1:
                yield node

    def roots(self):
        """
        Find roots in the graph
        """
        nodes = SortedDict()
        map(nodes.__setitem__, self.keys(), [])
        for node, deplist in self.items():
            for dep in deplist:
                nodes[dep] = True
        return [node for node, color in nodes.items() if not color]

    def traverse(self):
        """
        Perform a depth-first traverse of the graph
        """
        ret = SortedDict()
        level = self.roots()
        while len(level) > 0:
            nextlevel = SortedDict()
            for node in level:
                ret[node] = None
                # add dependencies to the next stack
                map(nextlevel.__setitem__, self[node], [])
            level = nextlevel.keys()
        return ret.keys()
    
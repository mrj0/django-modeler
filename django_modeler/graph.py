from django.utils.datastructures import SortedDict
try:
    from functools import reduce
except:
    pass

class Digraph(SortedDict):
    def __init__(self, roots=None):
        if roots:
            map(self.arc, roots)

    def __missing__(self, key):
        val = set()
        self[key] = val
        return val

    def arc(self, key, *depends_on):
        if key not in self:
            self[key] = set()

        self[key] = self[key].union(depends_on)
        for value in depends_on:
            # ensure there's a key for this dependency
            if not value in self:
                self[value] = set()

    def leafs(self):
        """
        Leafs don't depend on any other objects
        """
        ret = []
        for node, deplist in self.items():
            if not deplist or len(deplist) < 1:
                ret.append(node)
        return ret

    def roots(self):
        """
        Find roots in the graph. Nothing depends on a root.
        """
        nodes = SortedDict()
        map(nodes.__setitem__, self.keys(), [])
        for node, deplist in self.items():
            for dep in deplist:
                nodes[dep] = True
        return [node for node, color in nodes.items() if not color]

    def traverse(self):
        ret = SortedDict()
        level = self.roots()
#        for k, v in self.items():
#            print 'k', k, '\tlen:', len(v), '\tv', v
#        print 'graph', self
#        print 'roots', level
        while len(level) > 0:
            nextlevel = SortedDict()
            for node in level:
                if node not in ret:
                    ret[node] = None
                    # add dependencies to the next stack
                    map(nextlevel.__setitem__, self[node], [])
            level = nextlevel.keys()
        return ret.keys()

    ## {{{ http://code.activestate.com/recipes/577413/ (r1)
    def toposort2(self):
        if len(self) > 0:
            data = Digraph()
            map(data.__setitem__, self.keys(), self.values())

            for k, v in data.items():
                v.discard(k) # Ignore self dependencies
            extra_items_in_deps = reduce(set.union, data.values()) - set(data.keys())
            data.update({item:set() for item in extra_items_in_deps})
            while True:
                ordered = set(item for item,dep in data.items() if not dep)
                if not ordered:
                    break
                for el in ordered:
                    yield el
                data = {item: (dep - ordered) for item,dep in data.items()
                        if item not in ordered}
            assert not data, "A cyclic dependency exists amongst %r" % data
    ## end of http://code.activestate.com/recipes/577413/ }}}

#    def traverse(self):
#        """
#        Perform a topological sort of the tree
#        """
#        ret = SortedDict() # results may not be unique
#        graph = Digraph()
#        map(graph.__setitem__, self.keys(), self.values())
#
#        level = graph.roots()
#        print 'roots', level, 'for', graph
#
#        while len(level) > 0:
#            n = level.pop(0)
#            print 'adding n', n, n.__class__, 'deps', graph[n]
#            ret.insert(0, n, None)
#            for m in graph[n]:
#                # remove the arc from n to m
#                graph[n] = [e for e in graph[n] if e != m]
#                if len(graph[n]) < 1:
#                    ret.insert(0, n, None)
#                    next_level.append(m)
#            # print 'inserting self[n]', self[n]
#            map(ret.__setitem__, next_level, [])
#            level = list(set(level).union(next_level))
#            print 'level is now', level
#            print '-' * 40
#
#        arcs = sum(map(sum, graph.values()))
#        print 'graph is now', arcs
#        if arcs > 0:
#            raise ValueError, 'Cyclic dependency found.'
#        return ret.keys()

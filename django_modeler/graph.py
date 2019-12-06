from functools import reduce
import copy


class SortedDict(dict):
    """
    A dictionary that keeps its keys in the order in which they're inserted.
    """
    def __new__(cls, *args, **kwargs):
        instance = super(SortedDict, cls).__new__(cls, *args, **kwargs)
        instance.keyOrder = []
        return instance

    def __init__(self, data=None):
        if data is None or isinstance(data, dict):
            data = data or []
            super(SortedDict, self).__init__(data)
            self.keyOrder = list(data) if data else []
        else:
            super(SortedDict, self).__init__()
            super_set = super(SortedDict, self).__setitem__
            for key, value in data:
                # Take the ordering from first key
                if key not in self:
                    self.keyOrder.append(key)
                # But override with last value in data (dict() does this)
                super_set(key, value)

    def __deepcopy__(self, memo):
        return self.__class__([(key, copy.deepcopy(value, memo))
                               for key, value in self.items()])

    def __copy__(self):
        # The Python's default copy implementation will alter the state
        # of self. The reason for this seems complex but is likely related to
        # subclassing dict.
        return self.copy()

    def __setitem__(self, key, value):
        if key not in self:
            self.keyOrder.append(key)
        super(SortedDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        super(SortedDict, self).__delitem__(key)
        self.keyOrder.remove(key)

    def __iter__(self):
        return iter(self.keyOrder)

    def __reversed__(self):
        return reversed(self.keyOrder)

    def pop(self, k, *args):
        result = super(SortedDict, self).pop(k, *args)
        try:
            self.keyOrder.remove(k)
        except ValueError:
            # Key wasn't in the dictionary in the first place. No problem.
            pass
        return result

    def popitem(self):
        result = super(SortedDict, self).popitem()
        self.keyOrder.remove(result[0])
        return result

    def items(self):
        for key in self.keyOrder:
            yield key, self[key]

    def keys(self):
        for key in self.keyOrder:
            yield key

    def values(self):
        for key in self.keyOrder:
            yield self[key]

    def update(self, dict_):
        for k, v in dict_.items():
            self[k] = v

    def setdefault(self, key, default):
        if key not in self:
            self.keyOrder.append(key)
        return super(SortedDict, self).setdefault(key, default)

    def copy(self):
        """Returns a copy of this object."""
        # This way of initializing the copy means it works for subclasses, too.
        return self.__class__(self)

    def __repr__(self):
        """
        Replaces the normal dict.__repr__ with a version that returns the keys
        in their sorted order.
        """
        return '{%s}' % ', '.join('%r: %r' % (k, v) for k, v in six.iteritems(self))

    def clear(self):
        super(SortedDict, self).clear()
        self.keyOrder = []


class Digraph(SortedDict):
    def __init__(self, roots=None):
        if roots:
            list(map(self.arc, roots))

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
        for key in self.keys():
            nodes[key] = set()
        for node, deplist in self.items():
            for dep in deplist:
                nodes[dep] = True
        return [node for node, color in nodes.items() if not color]

    def traverse(self):
        ret = SortedDict()
        level = self.roots()
        while len(level) > 0:
            nextlevel = SortedDict()
            for node in level:
                if node not in ret:
                    ret[node] = None
                    # add dependencies to the next stack
                    for key in self[node]:
                        nextlevel[key] = set()
            level = list(nextlevel.keys())
        return list(ret.keys())

    ## {{{ http://code.activestate.com/recipes/577413/ (r1)
    def toposort2(self):
        if len(self) > 0:
            data = Digraph()
            list(map(data.__setitem__, self.keys(), self.values()))

            for k, v in data.items():
                v.discard(k) # Ignore self dependencies
            extra_items_in_deps = reduce(set.union, data.values()) - set(data.keys())
            data.update(dict([(k, set()) for k in extra_items_in_deps]))
            while True:
                ordered = set(item for item,dep in data.items() if not dep)
                if not ordered:
                    break
                for el in ordered:
                    yield el
                data = dict([(item, (dep - ordered)) for item,dep in data.items()
                        if item not in ordered])
            assert not data, "Data has a cyclic dependency"
    ## end of http://code.activestate.com/recipes/577413/ }}}

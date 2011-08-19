from django.test import TestCase
from django_modeler.graph import Digraph

class TestGraph(TestCase):
    def test_store(self):
        g = Digraph()
        g[1] = 2
        g[2] = 3
        g[3] = 2
        self.assertEqual(g[3], 2)

    def test_leafs(self):
        g = Digraph()
        g.arc(1, 2)
        g.arc(2, 3)
        g.arc(3, 2)
        g.arc(4)

        leafs = list(g.leafs())
        self.assertEqual([4], leafs)

    def test_roots(self):
        g = Digraph([1, 2, 3])
        g.arc(3, 4) # arc should create a key for 4
        self.assertEqual([1, 2, 4], list(g.leafs()))

    def test_find_roots(self):
        g = Digraph([1, 2, 3])
        g.arc(3, 4) # arc should create a key for 4
        # disconnected graph
        g.arc(6, 7)
        self.assertEqual([1, 2 , 3, 6], g.roots())

    def test_cyclic(self):
        g = Digraph()
        g.arc(1, 2)
        g.arc(2, 1)
        self.assertEqual([], g.roots())
        g.arc(3)
        self.assertEqual([3], g.roots())

    def test_traverse(self):
        g = Digraph()
        g.arc(1, 2)
        g.arc(2, 3)
        g.arc(3, 6)
        g.arc(4)

        self.assertEquals([1, 4, 2, 3, 6], list(g.traverse()))

    def test_dups(self):
        g = Digraph()
        g.arc(1, 2)
        g.arc(3, 2)
        g.arc(4, 2)
        self.assertEquals([1, 3, 4, 2], list(g.traverse()))
        g = Digraph()
        g.arc(1, 2)
        g.arc(3, 2)
        g.arc(4, 2)
        g.arc(2, 6)
        self.assertEquals([1, 3, 4, 2, 6], list(g.traverse()))

        g = Digraph()
        g.arc(1, 3)
        g.arc(3, 2)
        g.arc(4, 2)
        g.arc(2, 6)
        g.arc(15, 2) # root
        self.assertEquals([1, 4, 15, 3, 2, 6], list(g.traverse()))

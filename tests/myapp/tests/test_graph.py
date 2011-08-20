from django.test import TestCase
from django_modeler.graph import Digraph

class TestGraph(TestCase):
    def test_store(self):
        g = Digraph()
        g[1] = 2
        g[2] = 3
        g[3] = 2
        self.assertEqual(g[3], 2)

    def test_multiple(self):
        g = Digraph()
        g.arc(1, 2)
        g.arc(1, 3)
        self.assertEquals([2, 3], list(g[1]))
        self.assertTrue(2 in g)
        self.assertTrue(3 in g)

    def test_roots(self):
        g = Digraph([1, 2, 3])
        g.arc(3, 4) # arc should create a key for 4
        self.assertEqual([1, 2, 3], list(g.roots()))

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
        self.assertTrue(3 in g)
        self.assertEqual([3], g.roots())

    def test_traverse(self):
        g = Digraph()
        g.arc(1, 2)
        g.arc(2, 3)
        g.arc(3, 6)
        g.arc(4)

        self.assertEquals([1, 4], g.roots())
        self.assertEquals([1, 4, 2, 3, 6], list(g.traverse()))

    def test_dups(self):
        g = Digraph()
        #g.arc(1, 2)
        g.arc(3, 1, 2)
        g.arc(4, 1, 2, 3)
        self.assertEquals([4, 1, 2, 3], list(g.traverse()))

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
        g.arc(15, 2)
        self.assertEquals([1, 4, 15], g.roots())
        self.assertEquals([1, 4, 15, 3, 2, 6], list(g.traverse()))

        '''
reload(graph)
g = graph.Digraph()
g.arc(1, 3)
g.arc(3, 2)
g.arc(4, 2)
g.arc(2, 6)
g.arc(15, 2)
g.traverse()
'''
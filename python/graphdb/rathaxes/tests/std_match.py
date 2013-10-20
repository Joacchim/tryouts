#!/usr/bin/env python

from bulbs.neo4jserver import Graph
import rtx_graph
from rtx_tree_builder import *
import rtx_algo as Algos

def test():
    g = Graph()
    print "Initialized graph for standard match test..."
    rtx_graph.BuildGraphStructure(g)

    impl = RtxImplem()
    impl.addConfig("LKM::os",       "Windows")
    impl.addConfig("LKM::version",  "7")
    result = Algos.standard_match(g, "LKM::Context", impl)
    if len(result) != 5:
        print "[1] Found %i (instead of 5) matches for a standard match:" % len(result)
        for item in result:
            print "\t- " + str(item)
        return False

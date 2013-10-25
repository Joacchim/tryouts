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
    result = Algos.standard_match(g, "LKM::Context", impl, inclusive=False)
    if len(result) != 5:
        print "[STD][1] Found %i (instead of 5) matches for a standard match:" % len(result)
        for item in result:
            print "\t- " + str(item)
        return False
    result = Algos.standard_match(g, "LKM::Context", impl, inclusive=True)
    if len(result) != 6:
        print "[STD][1'] Found %i (instead of 6) matches for a standard match:" % len(result)
        for item in result:
            print "\t- " + str(item)
        return False

    impl = RtxImplem()
    result = Algos.standard_match(g, "LKM::Init()", impl, inclusive=False)
    if len(result) != 0:
        print "[STD][2] Found %i (instead of 0) matches for a standard match:" % len(result)
        for item in result:
            print "\t - " + str(item)
        return False
    result = Algos.standard_match(g, "LKM::Init()", impl, inclusive=True)
    if len(result) != 2:
        print "[STD][2'] Found %i (instead of 2) matches for a standard match:" % len(result)
        for item in result:
            print "\t - " + str(item)
        return False

    impl = RtxImplem()
    impl.addConfig("LKM::os",       "Linux")
    impl.addConfig("LKM::version",  "1")
    result = Algos.standard_match(g, "LKM::Init()", impl)
    if len(result) != 1:
        print "[STD][3] Found %i (instead of 1) matches for a standard match:" % len(result)
        for item in result:
            print "\t - " + str(item)
        return False

    impl = RtxImplem()
    impl.addConfig("LKM::os",       "Linux")
    impl.addConfig("LKM::version",  "5")
    result = Algos.standard_match(g, "LKM::Init()", impl)
    if len(result) != 1:
        print "[STD][4] Found %i (instead of 1) matches for a standard match:" % len(result)
        for item in result:
            print "\t - " + str(item)
        return False

    impl = RtxImplem()
    impl.addConfig("LKM::os",       "Linux")
    impl.addConfig("LKM::version",  "3")
    result = Algos.standard_match(g, "LKM::Init()", impl)
    if len(result) != 0:
        print "[STD][5] Found %i (instead of 0) matches for a standard match:" % len(result)
        for item in result:
            print "\t - " + str(item)
        return False

    return True

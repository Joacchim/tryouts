#!/usr/bin/env python

from bulbs.neo4jserver import Graph
import rtx_graph
from rtx_tree_builder import *
import rtx_algo as Algos

def test():
    g = Graph()
    print "Initialized graph."
    rtx_graph.BuildGraphStructure(g)

    #empty config
    impl = RtxImplem()
    if Algos.identity_match(g, "LKM::Context", impl) is None:
        print "[1] Found multiple matches for an identity match."
        return False

    # config with only one variable
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    if Algos.identity_match(g, "LKM::Context", impl) is None:
        print "[2] Found multiple matches for an identity match."
        return False

    # config with multiple variables
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  ">=",   "7")
    if Algos.identity_match(g, "LKM::Context", impl) is None:
        print "[3] Found multiple matches for an identity match."
        return False


    # config with multiple conditions on one variable
    # First on a no-other-configs tpl
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "FreeBSD")
    impl.addConstraint("LKM::version",  ">=",    "4")
    impl.addConstraint("LKM::version",  "<=",    "7")
    if Algos.identity_match(g, "LKM::Write(LKM::Context, Builtin::Buffer)",
                            impl) is None:
        print "[4] Found multiple matches for an identity match."
        return False

    # Then on a tpl with multiple configs
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  "<=",   "7")
    impl.addConstraint("LKM::version",  ">=",    "4")
    if Algos.identity_match(g, "LKM::Context", impl) is None:
        print "[5] Found multiple matches for an identity match."
        return False


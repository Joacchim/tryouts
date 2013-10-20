#!/usr/bin/env python

from tests import build_graph, identity_match, std_match
import rtx_algo

if __name__ == "__main__":
    print "Testing graph building..."
    build_graph.test()

    print "Testing identity match..."
    identity_match.test()

    print "Testing standard match..."
    std_match.test()

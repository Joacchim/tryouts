#!/usr/bin/env python

from tests import build_graph, identity_match

if __name__ == "__main__":
    print "Testing graph building..."
    build_graph.test()

    print "Testing identity match..."
    identity_match.test()


#!/usr/bin/env python

import string
from bulbs.neo4jserver import Graph
import rtx_graph
from rtx_tree_builder import *

dbg = True

def identity_match(g, signature, config):
    result = None

    request = "excepted_impls = new Table()\n"
    # Make sure that only the matching variables are present in the ref's constraints
    n_constraints = len(config.constraints())
    if n_constraints > 0:
        request += "g.V().filter{" + "it.element_type=='template' && it.signature=='{}'".format(signature) + "}.as('tpl')"
        request += ".out('implements').as('impl').out('selects').filter{ var ->"
        i = 0
        for name, value, op in config.constraints():
            if i != 0:
                request += "&&"
            request += " var.signature !='{}' ".format(name)
            i = i + 1

        request += "}.back('impl')"
        if dbg:
            try:
                result = g.gremlin.query(request)
                if result:
                    for ref in result:
                        print "Intermediate request: Excepting %s" % (ref)
                else:
                    print "Intermediate request: No tpl excepted."
            except Exception as inst:
                print inst
                dic = eval(inst[0][1])
                print ""
                print "[ERROR]: " + dic["message"]
                print ""
        request += ".fill(excepted_impls)\n"
        
    # Now, find matching decls, excluding the previous selection
    request += "g.V().filter{" + "it.element_type=='template' && it.signature=='{}'".format(signature) + "}.as('tpl')"
    request += ".out('implements').as('impl')"
    if dbg:
        try:
            result = g.gremlin.query(request)
            if result:
                for ref in result:
                    print "Intermediate Listing: Contains %s" % (ref)
            else:
                print "Intermediate Listing: No tpl."
        except Exception as inst:
            dic = eval(inst[0][1])
            print ""
            print "[ERROR]: " + dic["message"]
            print ""
    request += ".except(excepted_impls)"
    f = string.Template(".outE('selects').filter{it.value=='$val' && it.constraint=='$op'}"+
                ".inV().filter{it.signature=='$var'}"+
                ".back('impl')")
    for name, value, op in config.constraints():
        request += f.substitute(var=name, val=value, op=op)
        if dbg:
            print "Filtering on: '%s'" % (f.substitute(var=name, val=value, op=op))
            try:
                result = g.gremlin.query(request)
                if result:
                    for ref in result:
                        print "Intermediate request: Left %s" % (ref)
                else:
                    print "Intermediate request: No tpl left."
            except Exception as inst:
                dic = eval(inst[0][1])
                print ""
                print "[ERROR]: " + dic["message"]
                print ""


    if dbg: print "Request is: " + request
    try:
        result = g.gremlin.query(request)
    except Exception as inst:
        dic = eval(inst[0][1])
        print ""
        print "[ERROR]: " + dic["message"]
        print ""
        raise inst

    return result

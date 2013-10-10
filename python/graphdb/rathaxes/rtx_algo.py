#!/usr/bin/env python

import string
from bulbs.neo4jserver import Graph
import rtx_graph
from rtx_tree_builder import *

dbg = False

def identity_match(g, signature, config):
    result = None
    tmp_res = None

    request = "excepted_impls = new Table()\n"
    request += "g.V().filter{it.element_type=='template' && "+\
                "it.signature=='{}'".format(signature) + "}.as('tpl')"+\
                ".out('implements').as('impl').out('selects')"
    # Make sure that only the matching variables are present
    # in the ref's constraints
    n_vars = len(config.constraints())
    if n_vars > 0:
        request += ".filter{ var ->"
        i = 0
        for name in config.constraints():
            if i != 0:
                request += "&&"
            request += " var.signature !='{}' ".format(name)
            i = i + 1

        request += "}"

    request += ".back('impl')"
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

    # Make sure that matching variables with non-matching conditions
    # are excluded from the result set
    if n_vars > 0:
        for name in config.constraints():
            request += "g.V().filter{" + "it.element_type=='template' && "+\
                       "it.signature=='{}'".format(signature) + "}.as('tpl')"
            request += ".out('implements').as('impl')"
            request += ".outE('selects').filter{ val -> !( "
            first_constraint = True
            for value, op in config.constraints()[name]:
                if not first_constraint:
                    request += " || "
                request += "(val.value=='{}'".format(value)
                request += " && val.constraint=='{}')".format(op)
                first_constraint = False
            request += " ) }.inV().filter{ var -> "
            request += "var.signature=='{}'".format(name)
            request += " }.back('impl')"
            if dbg:
                try:
                    result = g.gremlin.query(request)
                    if result:
                        for ref in result:
                            print "Intermediate request 2:Excepting %s" % (ref)
                    else:
                        print "Intermediate request 2: No tpl excepted."
                except Exception as inst:
                    dic = eval(inst[0][1])
                    print ""
                    print "[ERROR]: " + dic["message"]
                    print ""
            request += ".fill(excepted_impls)\n"
        request += "\n"
        
    # Now, find matching decls, excluding the previous selection
    request += "g.V().filter{" + "it.element_type=='template' && "+\
               "it.signature=='{}'".format(signature) + "}.as('tpl')"
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
    f = string.Template(".outE('selects').filter{it.value=='$val' &&"+\
                        " it.constraint=='$op'}.inV().filter{"+\
                        "it.signature=='$var'}.back('impl')")
    for name in config.constraints():
        for value, op in config.constraints()[name]:
            request += f.substitute(var=name, val=value, op=op)
            if dbg:
                print "Filtering on: '%s'" %\
                    (f.substitute(var=name, val=value, op=op))
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

    if result is None:
        return None

    reslist = [ res for res in result ]
    if len(reslist) > 1:
        for res in reslist:
            print "Multiple choice result: %s" % (res)
        raise Exception("[Error] Could not identify an unique impl for "+\
                        "an identity match for config %s" %\
                        (config.constraints()))
    if len(reslist) == 0:
        return None

    return reslist[0]

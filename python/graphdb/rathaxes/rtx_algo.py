#!/usr/bin/env python

import string
from bulbs.neo4jserver import Graph
import rtx_graph
from rtx_tree_builder import *

dbg = False

def __debug_query(g, step, query):

    if dbg is not True:
        return

    print "Debugging Algorithms: " + step + ":"
    try:
        result = g.gremlin.query(query)
        if result:
            for ref in result:
                print "    Excepting %s" % (ref)
        else:
            print "    No tpl in result."
    except Exception as inst:
        print inst
        dic = eval(inst[0][1])
        print ""
        print "    [ERROR]: " + dic["message"]
        print ""
    print ""


def __setup_table(table_name):
    return table_name + " = new Table()\n"

def __filter_template_impls(signature):
    """
        Filter the template and retrieve all its implementations
    """
    return "g.V().filter{it.element_type=='template' && "+\
           "it.signature=='{}'".format(signature) + "}.as('tpl')"+\
           ".out('implements').as('impl')"

def __exclude_unmatched_parameters(g, signature, config, except_table):
    """
        Make sure that we exclude implementations providing values for
        parameters other than those within the config
    """
    request = __filter_template_impls(signature) + ".out('selects')"
    if len(config.constraints()) > 0:
        for name in config.constraints():
            request += ".filter{ "
            request += "var -> var.signature !='{}'".format(name)
            request += " }"
    request += ".back('impl')"

    __debug_query(g, "Exclude unmatched parameters", request)
    request += ".fill(" + except_table + ")\n"
    return request

def __exclude_non_identity_values(g, signature, config, except_table):
    request = ""
    # Make sure that matching variables with non-matching conditions
    # are excluded from the result set
    if len(config.constraints()) > 0:
        for name in config.constraints():
            subreq = __filter_template_impls(signature)
            subreq += ".outE('selects').filter{ val -> !( "
            first_constraint = True
            for value, op in config.constraints()[name]:
                if first_constraint is not True:
                    subreq += " || "
                subreq += "(val.value=='{}'".format(value)
                subreq += " && val.constraint=='{}')".format(op)
                first_constraint = False
            subreq += " ) }.inV().filter{ var -> "
            subreq += "var.signature=='{}'".format(name)
            subreq += " }.back('impl')"
            __debug_query(g, "Exclude unmatched values", subreq)
            request += subreq
            request += ".fill(" + except_table + ")\n"
        request += "\n"

    return request
        

def __select_identity_params(g, signature, config, except_table):
    # Now, find matching decls, excluding the previous selection
    request = __filter_template_impls(signature)
    __debug_query(g, "Selecting from full set", request)
    f = string.Template(".outE('selects').filter{it.value=='$val' &&"+\
                        " it.constraint=='$op'}.inV().filter{"+\
                        "it.signature=='$var'}.back('impl')")
    i = 1
    for name in config.constraints():
        for value, op in config.constraints()[name]:
            request += f.substitute(var=name, val=value, op=op)
            __debug_query(g, "Filtered Subset {} times".format(i), request)
            i += 1

    request += ".except("+except_table+")"
    return request

def __select_compatible_params(g, signature, config, except_table):
    request = ""
    all_impls = __filter_template_impls(signature)

    # First, exclude incompatible selections:
    #  - Any entry that does not comply with the constraint
    f = string.Template(".outE('selects').filter{ ! ("+\
                        "    (it.constraint == '<'  && '$val' <  it.value) "+\
                        " || (it.constraint == '<=' && '$val' <= it.value) "+\
                        " || (it.constraint == '==' && '$val' == it.value) "+\
                        " || (it.constraint == '>=' && '$val' >= it.value) "+\
                        " || (it.constraint == '>'  && '$val' >  it.value) "+\
                        ") }.inV().filter{it.signature=='$var'}.back('impl')")
    for name in config.constraints():
        for value, op in config.constraints()[name]:
            subreq = all_impls + f.substitute(var=name, val=value)
            __debug_query(g, "Excluding incompatible values for parameter " + name, subreq)
            request += subreq
            request += ".fill(" + except_table + ")\n"

    __debug_query(g, "Selecting compatible from full set", all_impls)

    # Now, find matching decls, excluding the previous selection
    request += all_impls + ".except(" + except_table + ")\n"

    return request


def identity_match(g, signature, config):
    result = None
    tmp_res = None
    except_table = "excepted_impls"

    request = __setup_table(except_table)
    request += __exclude_unmatched_parameters(g, signature, config, except_table)
    request += __exclude_non_identity_values(g, signature, config, except_table)
    request += __select_identity_params(g, signature, config, except_table)

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

def standard_match(g, signature, config):
    result = None
    except_table = "excepted_impls"

    # 1) Filter out any entry that restricts over an unused variable
    # (it should not be included by a configuration that does not specify the parameter)
    # 2) Filter out any entry which does not comply to all the constraints
    request = __setup_table(except_table)
    request += __exclude_unmatched_parameters(g, signature, config, except_table)
    request += __select_compatible_params(g, signature, config, except_table)

    print "dbg is %s" % (str(dbg))
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
        return []

    reslist = [ res for res in result ]
    return reslist

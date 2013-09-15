#!/usr/bin/env python

from collections import OrderedDict
from bulbs.utils import current_date
from bulbs.neo4jserver import Graph
import string
import rtx_graph
import rtx_algo as Algos
from rtx_tree_builder import *

dbg = False

def check_unique(generator, typestr, sign):

    if generator is None:
        raise Exception("%s %s cannot be found within the graph." %\
                        (typestr, sign))

    lst = [ ref for ref in generator ]
    if dbg: print lst
    if len(lst) > 1:
        raise Exception("%s %s is not unique within the graph." %\
                        (typestr, sign))

    return lst[0]

def generate_template_implem(g, tpl, tpl_node, implem):
    result = None
    impl_node = None

    result = Algos.identity_match(g, tpl.signature(), implem)

    if result is not None:
        impl_node = check_unique(result, "Implementation", tpl.signature())
        print impl_node
        if impl_node is not None:
            if dbg: print "Found impl for tpl %s" % (tpl.signature())
        else:
            print "Cannot find impl..."
            exit(0)
    else:
        print "Cannot find impl for tpl %s, config %s" %\
              (tpl.signature(), implem.constraints())
        exit(0)

    if impl_node is None:
        impl_node = g.implems.create(\
                source_file = tpl.signature()+"_{}.blt".format(implem.id()),
                ast_file    = tpl.signature()+"_{}.ast".format(implem.id()))
        g.implements.create(tpl_node, impl_node)
        for sign, val, op in implem.constraints():
            var_node = check_unique(g.variables.index.lookup(signature=sign),
                                    "Variable", sign)
            g.selects.create(impl_node, var_node, value=val, constraint=op)
            if dbg: print "Created constraint %s %s on %s" % (op, val, sign)
        if dbg: print "Created impl for tpl %s" %(tpl.signature())


def generate_template_data(g, tpl, tpl_node):

    for chunk in tpl.chunks():
        chunk_node = None
        ptct_node = None
        found = 0
        chks = tpl_node.outV("provides")
        if chks is not None:
            for chk in chks:
                ptcts = chk.outV("weave_in")
                for ptct in ptcts:
                    if ptct.signature == chunk:
                        chunk_node = chk
                        ptct_node = ptct
                        found = 1
                        break
                if found == 1:
                    break

        if found == 0:
            chunk_node = g.chunks.create()
            result = g.pointcuts.index.lookup(signature=chunk)
            if result is not None:
                lst = [ ref for ref in result ]
                if len(lst) > 1:
                    raise Exception("There should only be one pointcut '%s'" %\
                                    (chunk))
                ptct_node = lst[0]
            else:
                raise Exception("Pointcut for chunk %s could not be found "+\
                                "within the graph." % (chunk))
            g.provides.create(tpl_node, chunk_node)
            g.weave_in.create(chunk_node, ptct_node)

        if dbg: print "Chunk %s created for tpl %s" % (chunk, tpl.signature())


    """ Create the template's dependencies """
    for depSign in tpl.dependencies():
        deplist = tpl_node.outV("depends_on")
        depFound = 0
        if deplist is not None:
            for dep in deplist:
                if dep.signature == depSign:
                    depFound = 1
                    break
        if depFound == 0:
            if dbg: print "Creating Dep of Tpl %s on %s" %\
                          (tpl.signature(), depSign)
            refs = g.templates.index.lookup(signature=depSign)
            if refs is not None:
                deplist = [ dep for dep in refs]
                if len(deplist) > 1:
                    raise Exception("Too many templates matching the "+\
                                    "signature '%s'." % (depSign))
                dep_node = deplist[0]
            g.depends_on.create(tpl_node, dep_node)
        if dbg: print "Template '%s' depends on template '%s' properly." %\
                      (tpl.signature(), depSign)

    for implem in tpl.implementations():
        generate_template_implem(g, tpl, tpl_node, implem)


def generate_definitions(g, interface, itf_node):

    for var in interface.variables():
        var_node = None
        refs = g.variables.index.lookup(signature=var.signature())
        if refs is not None:
            varlist = [ ref for ref in refs ]
            if len(varlist) > 1:
                raise Exception("Too many variables matching the "+\
                                "signature '%s'." % (var.signature()))
            var_node = varlist[0]
        else:
            var_node = g.variables.create(signature=var.signature())
            g.describes.create(itf_node, var_node)
        if dbg: print "Created variable %s in the db: node %s" %\
                      (var.signature(), var_node)

    for ptct in interface.pointcuts():
        ptct_node = None
        refs = g.pointcuts.index.lookup(signature=ptct.signature())
        if refs is not None:
            ptctlist = [ ref for ref in refs ]
            if len(ptctlist) > 1:
                raise Exception("Too many pointcuts matching the "+\
                                "signature '%s'." % (ptct.signature()))
            ptct_node = ptctlist[0]
        else:
            ptct_node = g.pointcuts.create(signature=ptct.signature())
            g.describes.create(itf_node, ptct_node)
        if dbg: print "Created pointcut %s in the db: node %s" %\
                      (ptct.signature(), ptct_node)

    for tpl in interface.templates():
        tpl_node = None
        refs = g.templates.index.lookup(signature=tpl.signature())
        if refs is not None:
            tpllist = [ ref for ref in refs ]
            if len(tpllist) > 1:
                raise Exception("Too many templates matching the "+\
                                "signature '%s'." % (tpl.signature()))
            tpl_node = tpllist[0]
        else:
            tpl_node = g.templates.create(signature=tpl.signature())
            g.describes.create(itf_node, tpl_node)
        if dbg: print "Created template %s in the db: node %s" %\
                      (tpl.signature(), tpl_node)
        yield tpl, tpl_node


        

def generate_interface(g, interface):
    """ Create the interface """
    itf = g.interfaces.index.lookup(name=interface.name())
    if itf == None:
	    itf = g.interfaces.create(name=interface.name(),
                                  source_file=interface.name()+".rti",
                                  ast_file=interface.name()+".ast")
    else:
        itflist = [ node for node in itf ]
        if len(itflist) > 1:
            raise Exception("Too many interfaces matching the name '%s'" %\
                            (interface.name()))
        itf = itflist[0]

    for dep_name in interface.dependencies():
        create_dep = True
        deps = itf.outV('depends_on')
        if deps is not None:
            for dep in deps:
                if dep.name == dep_name:
                    create_dep = False
                    break
        if create_dep is True:
            dep_itf = None
            deps = g.interfaces.index.lookup(name=dep_name)
            if deps is not None:
                for dep in deps:
                    if dep.name == dep_name:
                        dep_itf = dep
                        break
            else:
                raise Exception("Dependency '%s' of interface '%s' could "+\
                                "not be found." % (dep_name, interface.name()))
            g.depends_on.create(itf, dep_itf)
            
	if dbg: print "Interface %s is in the db: node %s" % (itf.name, itf.eid)

    return itf



def generate_dataset(g, interface):

    itf_node = generate_interface(g, interface)

    for tpl, tpl_node in generate_definitions(g, interface, itf_node):
        generate_template_data(g, tpl, tpl_node)

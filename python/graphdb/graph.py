#!/usr/bin/env python

from collections import OrderedDict
from bulbs.model import Node, Relationship
from bulbs.property import Property, Document, Dictionary, String, Integer, DateTime
from bulbs.utils import current_date
from bulbs.neo4jserver import Graph
import string

class Interface(Node):
    element_type = "interface"
    
    name = String(nullable=False)

    source_file = String(nullable=False)
    ast_file = String(nullable=False)

class Template(Node):
    element_type = "template"
    signature = String(nullable=False)
    qualifier = Integer(nullable=False)

class TemplateImplem(Node):
    element_type = "implem"

    source_file = String(nullable=False)
    ast_file = String(nullable=False)

class ConfigVariable(Node):
    element_type = "variable"
    name = String(nullable=False)



class Describes(Relationship):   # Interface -> Template, ConfigVariable
    label = "describes"

class Depends(Relationship):     # Template -> Template or Variable -> Value
    label = "depends"

class Implements(Relationship):  # Template -> TemplateImplem
    label = "implements"

class Selects(Relationship):	 # TemplateImplem (value)-> ConfigVariable
    label = "selects"
    value_type = Integer(nullable=False)
    value = String(nullable=False)






def generate_dataset(g, itfSign, templates, variables, configs):

    """ Create the interface """
    origin = g.interfaces.index.lookup(name=itfSign)
    if origin == None:
	itf = g.interfaces.create(name=itfSign, source_file="itf1", ast_file="itf1.ast")
	print "Created interface %s" % (itfSign)
    else:
	itf = origin.next()
	print "Interface %s already is in the db: node %s" % (itfSign,itf.eid)

    """ Create the templates and their dependencies """
    for tplSign in templates.keys():
	origin = g.templates.index.lookup(signature=tplSign)
	if origin == None:
	    tpl = g.templates.create(signature=tplSign, qualifier=templates[tplSign]["qual"])
	    g.describes.create(itf, tpl)
	    print "Created Tpl %s" % (tplSign)
	else:
	    tpl = origin.next()
	    print "Tpl %s already is in the db: node %s" % (tplSign, tpl.eid)

        """ Create the template's dependencies """
	if templates[tplSign].has_key("deps"):
	    for depSign in templates[tplSign]["deps"]:
		origin = tpl.outV("depends")
		depFound = 0
		if origin is not None:
		    for dep in origin:
			if dep.signature == depSign:
			    print "Dependency of %s(%s) on %s(%s) already existed"%(tplSign,tpl.eid, depSign,dep.eid)
			    depFound = 1
			    break
		if depFound == 0:
		    print "Creating Dep of Tpl %s on %s" % (tplSign, depSign)
		    depTpls = g.templates.index.lookup(signature=depSign)
		    depTpl = depTpls.next()
		    print "dependency %s is node %s" % (depSign, depTpl.eid)
		    g.depends.create(tpl, depTpl)

    """ Create the variables """
    for varSign in variables:
	origin = g.variables.index.lookup(name=varSign)
	if origin == None:
	    var = g.variables.create(name=varSign)
	    g.describes.create(itf, var)
	    print "Created variable %s" % (varSign)
	else:
	    var = origin.next()
	    print "Variable %s already present: node %s" % (varSign, var.eid)
    
    """ Create the X implementations for each template """
    for tplSign in templates.keys():
        origin = g.templates.index.lookup(signature=tplSign)
	if origin == None:
	    print " ERROR: No template %s in db." % (tplSign)
	tpl = origin.next()
	print "Creating impl for tpl %s (%i)" % (tplSign, tpl.eid)
	origin = tpl.outV("implements")

        count = 0
        for config in configs:
	    
	
	    print ">>>> Trying gremlin..."
	    try:
		request = "g.v({}).out('implements').as('impl')".format(tpl.eid)
		print "Base request is '%s'" % (request)
		f = string.Template(".outE('selects').filter{it.value=='$val'}"+
				    ".inV().filter{it.name=='$var'}"+
				    ".back('impl')")
		for varName in config:
		    request += f.substitute(var=varName, val=config[varName])
		print "Base request is '%s'" % (request)
		result = g.gremlin.query(request)
		if result != None:
		    print ">>>> Gremlin found a matching template: %s" % (result)
		    for t in result:
			print t
	    except Exception as inst:
		for d in inst[0]:
		    print "d: %s" % (str(d))
	    print ">>>> gremlin done..."
	    
	    impl = None
	    if origin != None:
		for cur_impl in origin:
		    print "Testing implem %i" % (cur_impl.eid)
		    full_match = 1
		    constraints = cur_impl.outE("selects")
		    if constraints != None:
			for constr in constraints:
			    varv = constr.inV()
			    if varv == None:
				continue ;
			    print varv
			    print "  -> Testing Constraint: %s = %s" % (var.name, constr.value)
			    if config.has_key(var.name) and config[var.name] != constr.value:
				print "<- value does not match"
				full_match = 0
				break
			if full_match == 1:
			    print "Found similar template implementation"
			    impl = cur_impl	
			    break
		
	    if impl == None:
		print "New impl"
		impl = g.implems.create(source_file=tplSign+str(count)+".blt", ast_file=tplSign+str(count)+".ast")
		g.implements.create(tpl, impl)

		for varName in config:
		    print "Adding relationship to variable %s = %s" % (varName, config[varName])
		    varNode = g.variables.index.lookup(name=varName)
		    if varNode != None: # Null varNode means that it's associated to the current itf
			varNode = varNode.next()
			print "Adding relationship..."
			selector = g.selects.create(impl, varNode, value_type=0, value=config[varName])
		    else:
			print "Creating variable..."
			varNode = g.variables.create(name=varName)
			print "Creating describes relationship..."
			g.describes.create(itf, varNode)
			print "Adding relationship..."
			selector = g.selects.create(impl, varNode, value_type=0, value=config[varName])

	    else:
		print " Updating current impl"	

            count = count + 1

##

if __name__ == "__main__":
    g = Graph()
    print "Initialized graph."

    g.add_proxy("interfaces",    Interface)
    g.add_proxy("templates",     Template)
    g.add_proxy("implems",       TemplateImplem)
    g.add_proxy("variables",     ConfigVariable)

    g.add_proxy("describes",     Describes)
    g.add_proxy("depends",       Depends)
    g.add_proxy("implements",    Implements)
    g.add_proxy("selects",	 Selects)
    print "Added structure to graph"


    """
        For this test, we'll assume that the qualifier's value is:
        PROVIDED: 0
        REQUIRED: 1
        OPTIONAL: 2
    """
    generate_dataset(g,
                     "Builtin",
                     { "Builtin::String": { "qual": 0 },
                       "Builtin::Number": { "qual": 0 },
                       "Builtin::Serial": { "qual": 0 },
                       "Builtin::Buffer": { "qual": 0 }
                     },
		     {},
                     [ ]
                    )


    generate_dataset(g,
                     "LKM",
                     OrderedDict( [
			("LKM::Context", {
                                  "qual" : 0
                                }),
			("LKM::RegisterValue", {
                                  "qual" : 0
                                }),
			("LKM::Register", {
                                  "qual" : 0,
                                  "deps" : ["LKM::RegisterValue"]
                                }),
			("LKM::Init()", {
                                  "qual" : 0
                                }),
			("LKM::Open(LKM::Context)", {
                                  "qual" : 1,
                                  "deps" : ["LKM::Context"]
                                }),
			("LKM::Read(LKM::Context, Builtin::Buffer)", {
                                  "qual" : 2,
                                  "deps" : ["LKM::Context", "Builtin::Buffer"]
                                }),
			("LKM::Write(LKM::Context, Builtin::Buffer)", {
                                  "qual" : 2,
                                  "deps" : ["LKM::Context", "Builtin::Buffer"]
                                }),
			("LKM::Close(LKM::Context)", {
                                  "qual" : 1,
                                  "deps" : ["LKM::Context"]
                                }),
			("LKM::Fini(LKM::Context)", {
                                  "qual" : 1,
                                  "deps" : ["LKM::Context"]
                                })
                     ]),
		     {
			"Builtin::String" : [ "LKM::os" ],
			"Builtin::Number" : [ "LKM::version" ],

		     },
                     [
                        {
			  "LKM::os":	    "Linux",
                          "LKM::version":   "3"
                        },
			{
			 "LKM::os":	  "Windows",
                         "LKM::version":  "7"
			}
                     ])

    """
    itf = g.interfaces.create("Bus")
    tpl = g.templates.create("Bus::Context")
    g.describes(itf, tpl)
    tpl = g.templates.create("Bus::Probe(Builtin::String, Builtin::Serial)")
    g.describes(itf, tpl)
    tpl = g.templates.create("Bus::Register()")
    g.describes(itf, tpl)
    tpl = g.templates.create("Bus::Unregister(Bus::Context)")
    g.describes(itf, tpl)

    itf = g.interfaces.create("Network")
    tpl = g.templates.create("Network::Context")
    g.describes(itf, tpl)
    tpl = g.templates.create("Network::Register()")
    g.describes(itf, tpl)
    tpl = g.templates.create("Network::Unregister(Network::Context)")
    g.describes(itf, tpl)

    g.interfaces.create("Audio")
    """


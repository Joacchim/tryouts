#!/usr/bin/env python

from collections import OrderedDict
from bulbs.model import Node, Relationship
from bulbs.property import Document, String, Integer, DateTime
from bulbs.utils import current_date
from bulbs.neo4jserver import Graph

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

class ConfigValue(Node):
    element_type = "value"

    value = String(nullable=False)




class Describes(Relationship):   # Interface -> Template, ConfigVariable
    label = "describes"

class Depends(Relationship):     # Template -> Template or Variable -> Value
    label = "depends"

class Implements(Relationship):  # Template -> TemplateImplem
    label = "implements"

class Selects(Relationship):	 # ConfigValue -> TemplateImplem
    label = "selects"

class Specialises(Relationship): # ConfigVariable -> ConfigValue
    label = "specialises"






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
    
    return
    
    """ Create the X implementations for each template """
    for tplSign in templates.keys():
        origin = g.templates.index.lookup(signature=tplSign)
	if origin == None:
	    print " ERROR: No template %s in db." % (tplSign)
	tpl = origin.next()
	print "Creating impl for tpl %s" % (tplSign)
	origin = tpl.outV("implems")

        count = 0
        for config in configs:
	    is_present = 0
	    if origin != None:
		for cur_impl in origin:
		    constraints = cur_impl.outV("")
		
	    if is_present == 0:
		impl = g.implems.create(tplSign+string(count)+".blt", tplSign+string(count)+".ast")
		g.implements(tpl, impl)

		for var in config:
		    print "Adding relationship to variable %s = %s" % (var[0], var[1])
		    varNode = g.variables.index.lookup(name=var[0])
		    if varNode is null: # Null varNode means that it's associated to the current itf
			varNode = g.variables.create(name=var[0])
			g.describes.create(itf, varNode)


            count = count + 1

##

if __name__ == "__main__":
    g = Graph()
    print "Initialized graph."

    g.add_proxy("interfaces",    Interface)
    g.add_proxy("templates",     Template)
    g.add_proxy("implems",       TemplateImplem)
    g.add_proxy("variables",     ConfigVariable)
    g.add_proxy("values",        ConfigValue)

    g.add_proxy("describes",     Describes)
    g.add_proxy("depends",       Depends)
    g.add_proxy("implements",    Implements)
    g.add_proxy("specialises",   Specialises)
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
                        [
			  ["LKM::os", "Linux"],
                          ["LKM::version", "3"]
                        ],
                        [ ["LKM::os", "Windows"],
                          ["LKM::version", "7"]
                        ]
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


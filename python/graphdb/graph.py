from bulbs.model import Node, Relationship
from bulbs.property import Document, String, Integer, DateTime
from bulbs.utils import current_date

class Interface(Node):
    element_type = "interface"
    
    name = String(nullable=False)

    source_file = Document(nullable=False)
    ast_file = Document(nullable=False)

class Template(Node):
    element_type = "template"
    signature = String(nullable=False)
    qualifier = Integer(nullable=False)

class TemplateImplem(Node):
    element_type = "implem"

    source_file = Document(nullable=False)
    ast_file = Document(nullable=False)

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

class Specialises(Relationship): # ConfigVariable -> ConfigValue
    label = "specialises"




g = Graph()

g.add_proxy("interfaces",    Interface)
g.add_proxy("templates",     Template)
g.add_proxy("implems",       TemplateImplem)
g.add_proxy("variables",     ConfigVariable)
g.add_proxy("values",        ConfigValue)

g.add_proxy("describes",     Describes)
g.add_proxy("depends",       Depends)
g.add_proxy("implements",    Implements)
g.add_proxy("specialises",   Specialises)



def generate_dataset(g, itfSign, templates, variables, configs):

    """ Create the interface """
    itf = g.interfaces.create(itfSign)

    """ Create the templates """
    for tplSign in templates.keys():
        tpl = g.templates.create(tplSign, templates[tplSign]["qual"])
        g.describes.create(itf, tpl)

        """ Create the template's dependencies """
        for depSign in templates[tplSign]["deps"]:
            depTpl = g.templates.index.lookup(depSign)
            g.depends.create(tpl, depTpl)

    """ Create the variables """
    for varSign in variables:
        var = g.variables.create(varSign)
        g.describes.create(itf, var)
    
    """ Create the X implementations for each template """
    for tplSign in templates.keys():
        tpl = g.templates.index.lookup(tplSign)

        count = 0
        for config in configs:
            impl = g.implems.create(tplSign+string(count)+".blt", tplSign+string(count)+".ast")
            g.implements(tpl, impl)

            for var in config:
                varNode = g.variables.index.lookup(var[0])
                if varNode is null: # Null varNode means that it's associated to the current itf
                    varNode = g.variables.create(var[0])
                    g.describes.create(itf, varNode)


            count = count + 1

##

if __name__ = "__main__":
    """
        For this test, we'll assume that the qualifier's value is:
        PROVIDED: 0
        REQUIRED: 1
        OPTIONAL: 2
    """
    generate_dataset(g,
                     "Builtin",
                     { "String": { "qual": 0 },
                       "Number": { "qual": 0 },
                       "Serial": { "qual": 0 },
                       "Buffer": { "qual": 0 }
                     },
                     [ ]
                    )


    generate_dataset(g,
                     "LKM",
                     { "LKM::Context" : {
                                  "qual" : 0
                                },
                       "LKM::RegisterValue" : {
                                  "qual" : 0
                                },
                       "LKM::Register" : {
                                  "qual" : 0,
                                  "deps" : ["LKM::RegisterValue"]
                                },
                       "LKM::Init()" : {
                                  "qual" : 0
                                },
                       "LKM::Open(LKM::Context)" : {
                                  "qual" : 1,
                                  "deps" : ["LKM::Context"]
                                },
                       "LKM::Read(LKM::Context, Builtin::Buffer)" : {
                                  "qual" : 2,
                                  "deps" : ["LKM::Context", "Builtin::Buffer"]
                                },
                       "LKM::Write(LKM::Context, Builtin::Buffer)" : {
                                  "qual" : 2,
                                  "deps" : ["LKM::Context", "Builtin::Buffer"]
                                },
                       "LKM::Close(LKM::Context)" : {
                                  "qual" : 1,
                                  "deps" : ["LKM::Context"]
                                },
                       "LKM::Fini(LKM::Context)" : {
                                  "qual" : 1,
                                  "deps" : ["LKM::Context"]
                                }
                     },
                     [
                        [ ["itf::name", "value"],
                          ["itf::name", "value"]
                        ],
                        [ ["itf::name", "value"],
                          ["itf::name", "value"]
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


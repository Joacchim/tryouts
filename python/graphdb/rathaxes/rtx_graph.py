#!/usr/bin/env python

from bulbs.model import Node, Relationship
from bulbs.property import Property, Document, Dictionary, String, Integer, DateTime


##
## Available Graph Node types
##
class RtxGraphInterface(Node):
    element_type = "interface"
    name = String(nullable=False)
    source_file = String(nullable=False)
    ast_file = String(nullable=False)

class RtxGraphTemplate(Node):
    element_type = "template"
    signature = String(nullable=False)

class RtxGraphImplem(Node):
    element_type = "implem"
    source_file = String(nullable=False)
    ast_file = String(nullable=False)

class RtxGraphChunk(Node):
    element_type = "chunk"
    
class RtxGraphPointcut(Node):
    element_type = "pointcut"
    signature = String(nullable=False)

class RtxGraphVariable(Node):
    element_type = "variable"
    signature = String(nullable=False)



##
## Utility class (to constrain the comparison operator's string)
##
class RtxGraphConstraint(String):
    def _check_datatype(self, key, value):
        super._check_datatype(key, value)
        if  value != ">"  and value != ">=" and \
            value != "==" and \
            value != "<=" and value != "<":
            log.error("Type Error: '%s' is set to %s with type %s, but is not a comparison operator.", 
                      key, value, type(value), self.python_type)
            raise TypeError



##
## Available relationsships
##
class RtxGraphDescribes(Relationship):  # RtxGraphInterface -> RtxGraph{Template,Variable,Pointcut}
    label = "describes"

class RtxGraphDependsOn(Relationship):  # RtxGraphTemplate -> RtxGraphTemplate
    label = "depends_on"

class RtxGraphImplements(Relationship): # RtxGraphTemplate -> RtxGraphImplem
    label = "implements"

class RtxGraphSelects(Relationship):    # RtxGraphImplem -(value)-> RtxGraphVariable
    label = "selects"
    value = String(nullable=False)
    constraint = RtxGraphConstraint(nullable=False)

class RtxGraphProvides(Relationship):   # RtxGraphTemplate -> RtxGraphChunk
    label = "provides"

class RtxGraphWeaveIn(Relationship):    # RtxGraphChunk -> RtxGraphPointcut
    label = "weave_in"



def BuildGraphStructure(graph):

    # Add node types
    graph.add_proxy("interfaces",    RtxGraphInterface)
    graph.add_proxy("templates",     RtxGraphTemplate)
    graph.add_proxy("implems",       RtxGraphImplem)
    graph.add_proxy("chunks",        RtxGraphChunk)
    graph.add_proxy("pointcuts",     RtxGraphPointcut)
    graph.add_proxy("variables",     RtxGraphVariable)

    # Add relation types
    graph.add_proxy("describes",     RtxGraphDescribes)
    graph.add_proxy("depends_on",    RtxGraphDependsOn)
    graph.add_proxy("implements",    RtxGraphImplements)
    graph.add_proxy("selects",	     RtxGraphSelects)
    graph.add_proxy("provides",	     RtxGraphProvides)
    graph.add_proxy("weave_in",	     RtxGraphWeaveIn)

    print "Added structure to graph"

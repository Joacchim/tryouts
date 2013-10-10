#!/usr/bin/env python

from collections import OrderedDict
from bulbs.utils import current_date
from bulbs.neo4jserver import Graph
import string
import rtx_graph
import rtx_algo as Algos
from rtx_tree_builder import *
import generator


def input_data(g):
    itf = RtxInterface("Builtin")
    
    tpl = RtxTemplate("Builtin::String")
    impl = RtxImplem()
    tpl.addImplementation(impl)
    itf.addTemplate(tpl)
    
    tpl = RtxTemplate("Builtin::Number")
    impl = RtxImplem()
    tpl.addImplementation(impl)
    itf.addTemplate(tpl)
    
    tpl = RtxTemplate("Builtin::Serial")
    impl = RtxImplem()
    tpl.addImplementation(impl)
    itf.addTemplate(tpl)

    tpl = RtxTemplate("Builtin::Buffer")
    impl = RtxImplem()
    tpl.addImplementation(impl)
    itf.addTemplate(tpl)

    generator.generate_dataset(g, itf)



    itf = RtxInterface("LKM")

    itf.addDependency("Builtin")

    itf.addVariable(RtxVariable("LKM::os"))
    itf.addVariable(RtxVariable("LKM::version"))
    itf.addVariable(RtxVariable("LKM::serial"))
    
    itf.addPointcut(RtxPointcut("LKM::data_types()"))
    itf.addPointcut(RtxPointcut("LKM::prototypes()"))
    itf.addPointcut(RtxPointcut("LKM::code()"))


    tpl = RtxTemplate("LKM::Context")
    tpl.addChunk("LKM::data_types()")

    impl = RtxImplem()
    tpl.addImplementation(impl)

    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  ">=",    "7")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  "<=",    "7")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  "<=",    "7")
    impl.addConstraint("LKM::version",  ">=",    "4")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  "<=",    "7")
    impl.addConstraint("LKM::version",  ">=",    "4")
    impl.addConstraint("LKM::serial",   "==",    "DSHG-PEDS-JFLE-PREZ")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    tpl.addImplementation(impl)
    
    itf.addTemplate(tpl)


    tpl = RtxTemplate("LKM::RegisterValue")
    tpl.addChunk("LKM::data_types()")

    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  "==",    "5")
    tpl.addImplementation(impl)

    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    impl.addConstraint("LKM::version",  ">",    "5")
    tpl.addImplementation(impl)

    itf.addTemplate(tpl)
    

    tpl = RtxTemplate("LKM::Register")
    tpl.addDependency("LKM::RegisterValue")
    tpl.addChunk("LKM::data_types()")

    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  ">",    "6")
    tpl.addImplementation(impl)

    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    impl.addConstraint("LKM::version",  ">=",    "3")
    tpl.addImplementation(impl)

    itf.addTemplate(tpl)
    

    tpl = RtxTemplate("LKM::Init()")
    tpl.addChunk("LKM::prototypes()")
    tpl.addChunk("LKM::code()")
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    impl.addConstraint("LKM::version",  "<",    "2")
    tpl.addImplementation(impl)

    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    impl.addConstraint("LKM::version",  ">",    "4")
    tpl.addImplementation(impl)

    itf.addTemplate(tpl)
    

    tpl = RtxTemplate("LKM::Open(LKM::Context)")
    tpl.addDependency("LKM::Context")
    tpl.addChunk("LKM::prototypes()")
    tpl.addChunk("LKM::code()")

    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    impl.addConstraint("LKM::version",  "==",    "5")
    tpl.addImplementation(impl)
    
    itf.addTemplate(tpl)
    
    
    tpl = RtxTemplate("LKM::Read(LKM::Context, Builtin::Buffer)")
    tpl.addDependency("Builtin::Buffer")
    tpl.addDependency("LKM::Context")
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "OpenBSD")
    impl.addConstraint("LKM::version",  ">=",    "4")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    impl.addConstraint("LKM::version",  ">",    "4")
    tpl.addImplementation(impl)
    
    itf.addTemplate(tpl)
    
    
    tpl = RtxTemplate("LKM::Write(LKM::Context, Builtin::Buffer)")
    tpl.addDependency("Builtin::Buffer")
    tpl.addDependency("LKM::Context")
    tpl.addChunk("LKM::prototypes()")
    tpl.addChunk("LKM::code()")
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "FreeBSD")
    impl.addConstraint("LKM::version",  ">=",    "4")
    impl.addConstraint("LKM::version",  "<=",    "7")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "OpenBSD")
    impl.addConstraint("LKM::version",  ">",    "3")
    tpl.addImplementation(impl)
    
    itf.addTemplate(tpl)
    
    
    tpl = RtxTemplate("LKM::Close(LKM::Context)")
    tpl.addDependency("LKM::Context")
    tpl.addChunk("LKM::prototypes()")
    tpl.addChunk("LKM::code()")
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "OpenBSD")
    impl.addConstraint("LKM::version",  ">",    "3")
    tpl.addImplementation(impl)
    
    itf.addTemplate(tpl)
    

    tpl = RtxTemplate("LKM::Fini(LKM::Context)")
    tpl.addDependency("LKM::Context")
    tpl.addChunk("LKM::prototypes()")
    tpl.addChunk("LKM::code()")
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "OpenBSD")
    impl.addConstraint("LKM::version",  ">",    "3")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    impl.addConstraint("LKM::version",  ">",    "3")
    impl.addConstraint("LKM::version",  "<",    "6")
    tpl.addImplementation(impl)
    
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  ">",    "5")
    tpl.addImplementation(impl)
    
    itf.addTemplate(tpl)


    
    generator.generate_dataset(g, itf)



def test():
    g = Graph()
    print "Initialized graph."
    rtx_graph.BuildGraphStructure(g)

    input_data(g)

    #empty config
    impl = RtxImplem()
    if Algos.identity_match(g, "LKM::Context", impl) is None:
        print "[1] Found multiple matches for an identity match."
        return False

    # config with only one variable
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Linux")
    if Algos.identity_match(g, "LKM::Context", impl) is None:
        print "[2] Found multiple matches for an identity match."
        return False

    # config with multiple variables
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  ">=",   "7")
    if Algos.identity_match(g, "LKM::Context", impl) is None:
        print "[3] Found multiple matches for an identity match."
        return False


    # config with multiple conditions on one variable
    # First on a no-other-configs tpl
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "FreeBSD")
    impl.addConstraint("LKM::version",  ">=",    "4")
    impl.addConstraint("LKM::version",  "<=",    "7")
    if Algos.identity_match(g, "LKM::Write(LKM::Context, Builtin::Buffer)",
                            impl) is None:
        print "[4] Found multiple matches for an identity match."
        return False

    # Then on a tpl with multiple configs
    impl = RtxImplem()
    impl.addConstraint("LKM::os",       "==",   "Windows")
    impl.addConstraint("LKM::version",  "<=",   "7")
    impl.addConstraint("LKM::version",  ">=",    "4")
    if Algos.identity_match(g, "LKM::Context", impl) is None:
        print "[5] Found multiple matches for an identity match."
        return False


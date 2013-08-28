#!/usr/bin/env python

class RtxInterface:
    def __init__(self, name):
        self._name  = name
        self._deps  = []
        self._tpls  = []
        self._vars  = []
        self._ptcts = []

    def addDependency(self, dependency):
        self._deps.append(dependency)
        
    def addTemplate(self, tpl):
        self._tpls.append(tpl)

    def addVariable(self, var):
        self._vars.append(var)

    def addPointcut(self, ptct):
        self._ptcts.append(ptct)

    def name(self):
        return self._name

    def dependencies(self):
        return self._deps

    def variables(self):
        return self._vars

    def templates(self):
        return self._tpls

    def pointcuts(self):
        return self._ptcts


class RtxVariable:
    def __init__(self, signature):
        self._signature = signature

    def signature(self):
        return self._signature

class RtxPointcut:
    def __init__(self, signature):
        self._signature = signature

    def signature(self):
        return self._signature

class RtxTemplate:
    def __init__(self, signature):
        self._signature = signature
        self._deps = []
        self._impls = []

    def addImplementation(self, impl):
        self._impls.append(impl) 

    def addDependency(self, dependency):
        self._deps.append(dependency)

    def signature(self):
        return self._signature

    def dependencies(self):
        return self._deps

    def implementations(self):
        return self._impls

impl_id = 0

class RtxImplem:
    def __init__(self):
        global impl_id
        self._id = impl_id
        impl_id += 1
        self._config = []
        self._chunks = []

    def addConstraint(self, signature, op, value):
        self._config.append( (signature, value, op) )

    def addChunk(self, chunkSign):
        self._chunks.append(chunkSign)

    def constraints(self):
        return self._config

    def chunks(self):
        return self._chunks

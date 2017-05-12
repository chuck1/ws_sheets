import numpy
import traceback
import termcolor
import sys
import io

import sheets.script

APPROVED_MODULES = [
        "math",
        "numpy",
        ]

APPROVED_DEFAULT_BUILTINS = {
        '__build_class__': __build_class__,
        '__name__': 'module',
        "Exception": Exception,
        'globals': globals,
        'list': list,
        'object': object,
        'print': print,
        'range': range,
        "repr": repr,
        'sum': sum,
        "type": type,
        }

class Sheet(object):
    def __init__(self):
        self.cells = sheets.cells.Cells()
        
        self.script_pre = sheets.script.Script()
        self.script_post = sheets.script.Script()
    
    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in ['cells', 'script_pre', 'script_post'])
    
    def builtin___import__(self, name, globals=None, locals=None, 
            fromlist=(), level=0):
        
        name_split = name.split('.')
        
        if not name_split[0] in APPROVED_MODULES:
            raise ImportError("module '{}' is not allowed".format(name_split[0]))

        return __import__(name, globals, locals, fromlist, level)

    def ensure_size(self, r, c):
        if r > (numpy.shape(self.cells)[0]-1):
            shape = (r-numpy.shape(self.cells)[0]+1,numpy.shape(self.cells)[1])
            self.cells = numpy.append(
                    self.cells,
                    numpy.empty(shape,dtype=object),
                    axis=0)

        if c > (numpy.shape(self.cells)[1]-1):
            shape = (numpy.shape(self.cells)[0],c-numpy.shape(self.cells)[1]+1)
            self.cells = numpy.append(
                    self.cells,
                    numpy.empty(shape,dtype=object),
                    axis=1)

    def set_cell(self, r, c, s):
        self.ensure_size(r, c)

        if self.cells[r,c] is None:
            self.cells[r,c] = Cell(r,c)

        self.cells[r,c].set_string(self, s)

        self.do_all()

    def add_column(self, i):
        if i is None:
            i = numpy.shape(self.cells)[1]

        self.cells = numpy.insert(self.cells, i, None, axis=1)

    def add_row(self, i):
        if i is None:
            i = numpy.shape(self.cells)[0]

        self.cells = numpy.insert(self.cells, i, None, axis=0)

    def get_globals(self):
        if not hasattr(self, 'glo'):
            self.script_exec()
        return self.glo

    def reset_globals(self):
        approved_builtins = {
                '__import__': self.builtin___import__,
                }

        approved_builtins.update(APPROVED_DEFAULT_BUILTINS)

        self.glo = {
                "__builtins__": approved_builtins,
                "cells": self.cells_strings(),
                }

    def eval_all(self):
        
        self.cells_evaluated_set(False)

        def f(cell, r, c):
            if cell is None: return
            cell.calc(self)
        
        r = numpy.arange(numpy.shape(self.cells)[0])
        c = numpy.arange(numpy.shape(self.cells)[1])
        
        for i in range(numpy.shape(self.cells)[0]):
            for j in range(numpy.shape(self.cells)[1]):
                f(self.cells[i,j], r[i], c[j])

    def cells_evaluated_set(self, b):
        def f(c):
            if c is not None:
                c.evaluated = b
        numpy.vectorize(f)(self.cells)

    def cells_strings(self):
        def f(c):
            if c is None: return ""
            return c.string
        return numpy.array(numpy.vectorize(f, otypes=[str])(self.cells).tolist())

    def set_exec(self,s):
        if s == self.script: return
        self.script = s
        self.script_exec()


    def do_all(self):

        self.reset_globals()

        self.script_pre.execute(self.glo)

        self.cells_eval_all()

        self.script_post.execute(self.glo)
        



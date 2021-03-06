import logging

import codemach.machine

import ws_sheets.exception
import ws_sheets.middleware

logger = logging.getLogger(__name__)

class SecurityTest1(object):
    def call_book_globals(self, book, res):
        #print('called '+repr(self)+' call_book_globals g='+str(res._globals))
    
        self.MODULES_APPROVED = book.settings['middleware_security_modules_approved']
        self.BUILTINS_APPROVED = book.settings['middleware_security_builtins_approved']
        
        res._globals['__builtins__'].update(
                dict((name, __builtins__[name]) for name in self.BUILTINS_APPROVED))

        res._globals['__builtins__']['__import__'] = self.builtin___import__
                 
        #"sheets": dict((k, s.cells_strings()) for k, s in self.sheets.items()),
         
        res._globals['book'] = book
  
    def builtin___import__(
            self, 
            name, 
            globals=None, 
            locals=None, 
            fromlist=(), 
            level=0):
        
        name_split = name.split('.')
        
        if not name_split[0] in self.MODULES_APPROVED:
            raise ImportError("module '{}' is not allowed".format(name_split[0]))

        return __import__(name, globals, locals, fromlist, level)

    def builtin_open(self, file, mode='r'):
        logger.warning("invoking Book.builtin_open({}, {})".format(file, mode))

        #file = open(file, mode)

        test_fs = fs.osfs.OSFS(os.path.join(os.environ['HOME'], 'web_sheets','filesystems','test'))
        file = test_fs.open(file, mode)

        return WrapperFile(file)

    def builtin_getattr(self, *args):
        logger.warning("invoking Book.builtin_getattr({})".format(args))
        obj = args[0]
        logger.warning("obj={}".format(obj))
        
        # temporarily removed for teting of special helper module importing
        """
        import sheets.helper
        if isinstance(obj, sheets.helper.CellsHelper):
            raise sheets.exception.NotAllowedError(
                    "For security, getattr not allowed for CellsHelper objects")
        """

        return getattr(*args)

    def call_book_method_decorator(self, book, f, args):
        return
        
        context = object.__getattribute__(book, 'context')

        if f.__name__ == '__getattribute__':
            if not args[0] in ['__getitem__', 'sheets']:
                raise ws_sheets.exception.NotAllowedError(
                        "stopped by protector in context {}. {}({})".format(
                            context, f.__name__, args))


    def call_sheet_globals(self, book, sheet, res):
        res._globals = dict(book.get_globals())

        res._globals.update({
            'sheet': sheet,
            })

        """
        filename = os.path.join(os.path.dirname(sheets.__file__), 'helper.py')
        
        with open(filename) as f:
            exec(f.read(), self.glo)
        """

    def call_check_script_code(self, script):
        pass

    def call_check_cell_code(self, cell):
        """
        If any of the values in co_names contains ``__``, a
        :py:exc:`sheets.exception.NotAllowedError` is raised.
        """

        if cell.code is None: return
        
        if False: # turn off to test other security measures
            for name in cell.code.co_names:
                if '__' in name:
                    raise ws_sheets.exception.NotAllowedError(
                            "For security, use of {} is not allowed".format(name))


    def call_cell_eval(self, book, cell, code, _globals, res):

        e = codemach.machine.Machine(code)

        with ws_sheets.context.context(book, ws_sheets.context.Context.CELL):
            res.return_value = e.execute(_globals)

    def call_script_exec(self, book, script, code, _globals, res):
        logger.debug('{} call_script_exec'.format(self.__class__.__name__))

        m = codemach.machine.Machine(code)

        def load_attr(thing, name):
            if thing is book:
                if not name in ():
                    raise ws_sheets.exception.NotAllowedError(
                            "for security, get attribute {} of {} is forbidden".format(
                                name, thing))

        def call_function(f, *args):
            if (f is getattr) or (f is object.__getattribute__):
                load_attr(*args)

        def import_name(name, *args):
            name_split = name.split('.')
        
            if not name_split[0] in self.MODULES_APPROVED:
                raise ws_sheets.exception.NotAllowedError(
                        "module '{}' is not allowed".format(name_split[0]))

        m.add_callback('LOAD_ATTR', load_attr)
        m.add_callback('CALL_FUNCTION', call_function)
        m.add_callback('IMPORT_NAME', import_name)

        with ws_sheets.context.context(book, ws_sheets.context.Context.CELL):
            #exec(code, _globals)
            m.execute(_globals)






import re
import pprint

pp = pprint.PrettyPrinter(indent=4)

def tester(testRun, implementation):
    #print 'entering testrun'
    testRun.result = False
    local_scope = {}
    global_scope = get_global_scope()
    try:
        #print 'entering implementationrun'
        #pp.pprint(global_scope)
        #pp.pprint(local_scope)
        print replace_dangerous_statements(remove_carriage_return(implementation.code))# in global_scope, local_scope
        #exec replace_dangerous_statements(remove_carriage_return(testRun.implementation.code)) in global_scope, local_scope
        
        try:
            #print 'entering testrun'
            #pp.pprint(global_scope)
            #pp.pprint(local_scope)
            exec remove_carriage_return(testRun.test.code) in global_scope.update(local_scope), local_scope
            testRun.result = True
        except AssertionError, inst:
            testRun.error = "Assertion failed: " + str(inst);
        except SyntaxError, inst:
            testRun.error = "Parsing the test failed: " + str(inst);
        except Exception, inst:
            testRun.error = "Running the test failed: " + str(inst);

    except SyntaxError, inst:
        testRun.error = "Parsing the implementation failed: " + str(inst);
    except Exception, inst:
        testRun.error = "Couldn't execute your implementation: " + str(inst);
    
    return testRun

def replace_dangerous_statements(code):
    p = re.compile( '(\W|^)(eval|exec|import)(\W|$)')
    return p.sub( '#', code)

def remove_carriage_return(input):
    return input.replace("\r", ""); 

def get_global_scope():
    global_scope = {}
    global_scope['__builtins__'] = {}
    #print 'entering get_global_scope'
    whitelist = ['bytearray','IndexError','all','help','vars','SyntaxError','unicode','UnicodeDecodeError','isinstance', 'hasattr', 'getattr'
                 'copyright','NameError','BytesWarning','dict','oct','bin','StandardError','format','repr','sorted','False',
                 'RuntimeWarning','list','iter','Warning','round','cmp','set','bytes','reduce','intern','issubclass','Ellipsis',
                 'EOFError','BufferError','slice','FloatingPointError','sum','abs','print','True','FutureWarning','ImportWarning',
                 'None','hash','ReferenceError','len','credits','frozenset','ord','super','TypeError','license','KeyboardInterrupt',
                 'UserWarning','filter','range','staticmethod','SystemError','BaseException','pow','RuntimeError','float',
                 'MemoryError','StopIteration','divmod','enumerate','apply','LookupError','basestring','UnicodeError','zip','hex',
                 'long','next','ImportError','chr','xrange','type','Exception','tuple','UnicodeTranslateError','reversed',
                 'UnicodeEncodeError','IOError','SyntaxWarning','ArithmeticError','str','property','GeneratorExit','int','KeyError',
                 'coerce','PendingDeprecationWarning','EnvironmentError','unichr','id','OSError','DeprecationWarning','min',
                 'UnicodeWarning','any','complex','bool','ValueError','NotImplemented','map','buffer','max','object','TabError',
                 'ZeroDivisionError','IndentationError','AssertionError','classmethod','UnboundLocalError','NotImplementedError',
                 'AttributeError','OverflowError','WindowsError','__name__']
    
    for key in __builtins__:
        if key in whitelist:
            global_scope['__builtins__'][key] = __builtins__[key]
    
    return global_scope
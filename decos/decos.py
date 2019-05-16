import functools
import time,os,sys,pdb
import inspect

__all__ = ["timer","debug","safe_run"]

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug


def safe_run(_func=None,*,dcs={}):
    """ Tries to run the function and throws the given error(argument)
    dcs['tb']: String to print in try block
    dcs['cb']: String to print in except block
    dcs['dv']: default value to return: default is None
    dcs['var']: var to be printed with cb
    """
    def saferun(func):

        def get_def_kwargs(*ar,**kw):
            vals = inspect.getargspec(func)
            def_kwargs = {}
            if vals[3]:
                def_kwargs = dict(zip(vals[0][-(vals[3].__len__()):],vals[3]))
            
            mod_arg = dict(zip(vals[0][:len(ar)],ar))
            for k,v in mod_arg.items():
                def_kwargs[k] = v
            
            return def_kwargs

        def handle_vars(cb,def_kwargs):
            if not dcs.get('var',None):
                return cb
            for var in dcs.get('var'):
                if def_kwargs.get(var,None):
                    cb = cb + f' {var} = {str(def_kwargs[var])} '
            return cb
        
        def handler(*ar,**kw):
            tb = f"Running the function {func.__name__} " if dcs.get('tb',None) is None else dcs.get('tb')
            cb = f"Something wrong happened while running {func.__name__} -- " if dcs.get('cb',None) is None else dcs.get('cb')
            all_ar = get_def_kwargs(*ar,**kw)
            cb = handle_vars(cb,all_ar)
            return tb,cb

        @functools.wraps(func)
        def try_run_function(*args,**kwargs):
            tb,cb = handler(*args,**kwargs)
            try:
                print(tb)
                value = func(*args,**kwargs)
                return value
            except Exception as e:
                print(cb+f'{e}'+f' More info over here... \n{sys.exc_info()}')
                return dcs.get('dv',None)
        
        return try_run_function
    
    if dcs.get('var',None):
        assert isinstance(dcs['var'],list),('value of var must be a list')
    if _func is None:
        return saferun
    else:
        return saferun(_func)

from simplads.simplad_monad.simplad_monad import SimpladResult
from simplads import ErrorDeltaMaker

def rn(i):
    return SimpladResult(val=i, delta_map={})

def error(value, error):
    print('retu')
    return SimpladResult(val=value, delta_map={'error': ErrorDeltaMaker.error(error)})

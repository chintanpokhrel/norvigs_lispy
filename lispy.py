import math
import operator as op

#Types
Symbol = str
Number = (int, float)
Atom = (Symbol, Number)
List = list
Exp = (Atom, List)
Env = dict

#Tokenizer
def tokenize(chars: str)->list:
  return chars.replace('(', ' ( ').replace(')', ' ) ').split()

#Parser
def parse(program: str)->Exp:
  return read_from_tokens(tokenize(program))

def read_from_tokens(tokens: list)->Exp:
  if len(tokens) == 0:
    raise SyntaxError("Unexpected EOF")

  token = tokens.pop(0)
  if token == "(":
    L = []
    while tokens[0] != ")":
      L.append(read_from_tokens(tokens))
    tokens.pop(0)
    return L
  elif token == ")":
    raise SyntaxError("Unexpected )")
  else:
    return atom(token)

def atom(token: str)->Atom:
  try: return int(token)
  except ValueError:
    try: return float(token)
    except ValueError:
      return Symbol(token)

#Standard environment
class Env(dict):
  "An environment: a dict of {'var': val} pairs, with an outer env"
  def __init__(self, params=(), args=(), outer=None):
    self.update(zip(params, args))
    self.outer = outer

  def find(self, var):
    "Find the innermost Env where var appears"
    return self if (var in self) else self.outer.find(var)

class Procedure(object):
  "A user defined Scheme function"
  def __init__(self, params, body, env):
    self.params, self.body, self.env = params, body, env
  def __call__(self, *args):
    return eval(self.body, Env(self.params, args, self.env))

    
def standard_env() -> Env: 
  "An environment with some Scheme std procs"
  env = Env()
  env.update(vars(math))
  env.update({
    '+': op.add,
    '-': op.sub,
    '*': op.mul,
    '/': op.truediv,
    '>': op.gt,
    '<': op.lt,
    '>=': op.ge,
    '<=': op.le,
    '=': op.eq,
    'abs': abs,
    'append': op.add,
    'apply': lambda proc, args: proc(*args),
    'begin': lambda *x:  x[-1],
    'car': lambda x: x[0],
    'cdr': lambda x: x[1:],
    'cons': lambda x,y:[x]+y,
    'eq?': op.is_,
    'expt': pow,
    'equal?': op.eq,
    'length': len,
    'list?': lambda x: isinstance(x, List),
    'map': map,
    'max': max,
    'min': min,
    'not': op.not_,
    'null?': lambda x: x == [],
    'number?': lambda x: isinstance(x, Number),
    'print': print,
    'procedure?': callable,
    'round': round,
    'symbol?': lambda x: isinstance(x, Symbol),
  })
  
  return env

global_env = standard_env()

def eval(x: Exp, env=global_env)->Exp:
  if isinstance(x, Symbol):
    return env.find(x)[x]
  elif not isinstance(x, List):
    return x
  
  op, *args = x
  if op == 'quote':
    return args[0]
  elif op == 'if':
    (test, conseq, alt) = args
    exp = (conseq if eval(test, env) else alt)
    return eval(exp, env)
  elif op == 'define':
    (symbol, exp) = args
    env[symbol] = eval(exp, env)
  elif op == 'set!':
    (symbol, exp) = args
    env.find(symbol)[symbol] = eval(exp, env)
  elif op == 'lambda':
    (params, body) = args
    return Procedure(params, body, env)
  else:
    proc = eval(op, env)
    vals = [eval(arg, env) for arg in args]
    return proc(*vals)

def repl(prompt = 'lispy> '):
  "A prompt-read-eval-print loop"
  while True:
    user_input = input(prompt)
    if len(user_input.strip()) > 0:
      try:
        val = eval(parse(user_input))
        if val is not None:
          print(schemestr(val))
      except Exception as e:
          print(schemestr(e))

def schemestr(exp):
  "Convert a Python object back to a Scheme-readable string"
  if isinstance(exp, List):
    return '(' + ' '.join(map(schemestr, exp)) + ')'
  else:
    return str(exp)
 

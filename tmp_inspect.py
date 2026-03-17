from symbolic_simplifier.engine import detect_method
from symbolic_simplifier.parser import parse_expression

expr = parse_expression('(x+1)(x+3)')
print('expr:', expr, type(expr))
method_lines, rule_steps = detect_method(expr)
print('method_lines:', method_lines)
print('rule_steps:', rule_steps)

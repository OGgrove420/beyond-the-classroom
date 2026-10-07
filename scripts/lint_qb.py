import ast
src = open('/opt/data/learning-app/api/question_bank.py').read()
try:
    ast.parse(src)
    print('OK')
except SyntaxError as e:
    print('SYNTAX ERROR line', e.lineno, ':', e.msg)

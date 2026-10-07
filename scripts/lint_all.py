import ast
for f in ['/opt/data/learning-app/api/index.py', '/opt/data/learning-app/api/question_bank.py',
          '/opt/data/learning-app/api/grades.py', '/opt/data/learning-app/api/payments.py']:
    try:
        ast.parse(open(f).read())
        print(f.split('/')[-1], 'OK')
    except SyntaxError as e:
        print(f.split('/')[-1], 'SYNTAX ERROR line', e.lineno, ':', e.msg)

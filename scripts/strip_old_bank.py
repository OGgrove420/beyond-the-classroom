"""Strip the old in-file QUIZ_BANK (superseded by question_bank.py bands)."""
lines = open('/opt/data/learning-app/api/index.py').read().splitlines(keepends=True)
# QUIZ_BANK starts at line 73 (1-indexed) and closes with "]" at 179
assert lines[72].startswith('QUIZ_BANK'), lines[72]
assert lines[178].rstrip() == ']', lines[178]
new = lines[:72] + lines[179:]
open('/opt/data/learning-app/api/index.py', 'w').write(''.join(new))
print('stripped', 179 - 72, 'lines; new total', len(new))

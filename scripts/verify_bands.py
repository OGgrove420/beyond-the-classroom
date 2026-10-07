import sys
sys.path.insert(0, '/opt/data/learning-app/api')
import question_bank as qb
for band, qs in qb.BANK.items():
    print(band, len(qs), [q['subject'] for q in qs])
import grades as g
for t in ['Grade R', 'grade 3', 'Grade 6', '8', 'Grade 11', 'banana']:
    info = g.grade_info(t)
    print(t, '->', (info['band'], info['intensity']['label']) if info else None)

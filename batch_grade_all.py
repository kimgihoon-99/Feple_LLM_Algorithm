import os
import sys

# 실행할 평가 파일 목록 (루트에서 실행, 하위 폴더 경로 포함)
scripts = [
    'absolute_grading/grade_politeness_auto.py',
    'absolute_grading/grade_empathy_auto.py',
    'absolute_grading/grade_emotional_stability_auto.py',
    'absolute_grading/grade_stability_auto.py',
    'absolute_grading/grade_problem_solving.py',
]

for script in scripts:
    print(f'\n===== 실행: {script} =====')
    exit_code = os.system(f'{sys.executable} {script}')
    if exit_code != 0:
        print(f'오류 발생: {script}') 
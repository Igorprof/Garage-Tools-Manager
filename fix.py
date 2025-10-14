with open('requirements.txt', 'r', encoding='utf-8') as f:
    data = f.readlines()

res = []
for row in data:
    res.append('=='.join(row.split()))

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(res))
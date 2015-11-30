import re
import codecs

line_seg = ''
chars = set()
with codecs.open('/home/daniel/data/companies.csv', 'rU', 'utf-8') as fin:
    with open('/home/daniel/data/companies-clean.csv', 'w') as fout:
        for line in fin.readlines():
            line = line.strip().replace(u'\ufffd', '')
            for c in line:
                chars.add(c)
            if not line:
                continue
            if re.match(r'"(?!,)', line):
                line_seg = line
            else:
                line = line_seg + line
                fout.write(line + '\n')

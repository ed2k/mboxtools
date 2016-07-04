import re


def is_email_tabs(s):
    m = re.match("[ \t>]+", s)
    return not m is None

def toremove_breaks(s, to_remove):
    t = to_remove.strip()
    s2 = s[:len(to_remove)]
    if len(t) > 0:
        return s2.strip()[:len(t)] != t
    return s2 != to_remove

def fix_column_format(s):
  changed = True
  ss = s.splitlines()
  while changed:
    changed = False
    idx = 0
    r = []
    for line in ss:
        if idx < 1:
            idx = line.find('From: ')
            if idx > 0: 
                  to_remove = line[:idx]
                  if is_email_tabs(to_remove):
                      print('to_remove', [to_remove])
                      changed = True
                      line = line[idx:]
                  else: 
                      idx = 0
        else:
            if toremove_breaks(line, to_remove):
                idx = 0
            else: line = line[idx:]
        r.append(line)
    ss = r
  return '\n'.join(ss)

def fix_column_format2(s):
	# get proper format
	while s.find('\n\xa0\n') >=0: s = s.replace('\n\xa0\n', '\n\n')
	while s.find(' \n') >=0: s = s.replace(' \n', '\n')
	changed = True
	while changed:
		changed = False
		while s.find('\n\n\n') >=0: s = s.replace('\n\n\n', '\n\n')
		# get \n\n section
		sections = s.split('\n\n')
		r = []
		for sec in sections:
			n = fix_col_section(sec)
			r.append(n)
			if n != sec: changed = True
		s = '\n\n'.join(r)
  	return s

def fix_col_section(section):
	ss = section.splitlines()
	if len(ss) < 2: return section

	while True:
		if len(ss[0]) < 1: return section
		first = ss[0][0]
		for line in ss[1:]:
			if len(line) < 1: return section
			second = line[0]
			if first != second: return section
		r = []
		for line in ss: r.append(line[1:])
		ss = r
		section = '\n'.join(r)

def fix_field_name(s):
	s = s.strip()
	if s[-1] == '*': s = s[:-1]
	return s

def fix_field_body(s):
	s = s.strip()
	if len(s) <= 0: return s
	if s[0] == '*': s = s[1:]
	return ' '+s.strip()

OM = '-Original Message-'
def fix_header(s):
	r = []
	sections = s.split('\n\n')
	for sec in sections:
		headers = 0
		noheaders = 0
		lines = sec.splitlines()
		for line in lines:
			if line.find(':') < 1:
				noheaders += 1
			else: headers += 1
		if headers < noheaders or headers == 0:
			r.append(sec)
			continue
		print(headers,noheaders,lines)
		if lines[0].find(OM) >= 0: lines = lines[1:]
		n = lines[0].split(':')
		if len(n) < 2:
			r.append(sec)
			continue
		ch = fix_field_name(n[0])
		h = [ch+':'+fix_field_body(':'.join(n[1:]))]
		for line in lines[1:]:
			n = line.split(':')
			if len(n) < 2:
				h[-1] = h[-1]+';'+fix_field_body(line)
			else:
				ch = fix_field_name(n[0])
				h.append(ch+':'+fix_field_body(':'.join(n[1:])))
		r.append('\n'.join(h))
	return '\n\n'.join(r)


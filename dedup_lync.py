#!/usr/bin/env python
"""  sorted by same subject, remove duplication
"""

import email
from email.MIMEText import MIMEText
import sys, os, string, re

LF = '\x0a'
F_CHAT = "\n[^\[]+\[\d+:\d+ ['A'|'P']M\]: *\n"
F_CONV = "Conversation with "

def check_n_append(r, contents, k, v):
    if not k in r:
               r[k] = v
               contents.append(k)
               contents.append(v)
    elif r[k].find(v) < 0:
               r[k] += ('\n'+v)
               contents.append(k)
               contents.append(v)

# pattern, \nName1 Name2 [n+:n+ AM]: *\nor PM
def parse_chat_items(s, r):
    s = s.replace('\r\n', '\n')
    s = '\n'+s
    while s.find('\n\n') >= 0: s = s.replace('\n\n', '\n')
    s.strip()
    contents = []
    start = 0
    m = None
    while start < len(s):
        m = re.search(F_CHAT, s[start:])
        if m is None:
           #print ('!!!left out:', s[start:start+100])
           check_n_append(r, contents, 'UNKNOWN SPEAKER [67:89 PM]: ', s[start:])
           return '\n'.join(contents)
        if m.start(0) != 0: print(m.start(0),m.end(0),'--:',s[start:start+m.end(0)])
        start +=  m.end(0)
        k = m.group(0).strip()
        n = re.search(F_CHAT, s[start:])
        if n is None:
           v = s[start:].strip()
           start = len(s)
        else:
           v = s[start:start+n.start(0)].strip()
           start += (n.start(0))
           m = n
        check_n_append(r, contents, k, v)
    return '\n'.join(contents)

def dedup_chats(items):
    chat = {}
    new_msgs = []
    for msg in items:
        all_chats = parse_chat_items(msg.get_payload(), chat)
        #print('chats:',[all_chats])
        if all_chats != '': 
            msg.set_payload(all_chats)
            new_msgs.append(msg)
    return new_msgs

def same_subject(s1, s2):
    #TODO use sequence matcher to catalog similar subject
    # such as ignore tab, space etc.
    # lync chat with subject Conversation with, what to do?
    if len(s1) < len(s2): s = s1; s1 = s2
    elif len(s1) == len(s2): return s1 == s2

    prefix = s1[0:3].upper()
    return (prefix =='RE: ' or prefix=='FW: ') and s == s1[4:]
    
def main ():
    mailboxname_in = sys.argv[1]

    # Open the mailbox.
    mbstr = file(mailboxname_in,'r').read();
    # mbstr = mbstr.replace('\r\n','\n');
    mails = mbstr.split("\nFrom - ");

    # assume no multipart, otherwise run split_attachements first
    for idx, mail in enumerate(mails):
        #take out the first line
        i = mail.find("\n");
        mails[idx] =email.message_from_string( mail[i+1:]);
        if mails[idx].is_multipart():
            print  "ERROR, run mail split first"
            break
    print 'read in', len(mails)

    # fix some no subject emails
    for idx, msg in enumerate(mails):
        sub = msg['Subject'];
        if sub is None: sub = ''
        if len(sub) > 5:
            sub = sub.replace('\n','')
            sub = sub.replace('\t','')
            sub = sub.replace('  ',' ')
            msg.replace_header('Subject',sub)
            continue
        
        #makeup subject
        body = msg.get_payload();
        end_pos = body.find('\.')
        if end_pos == -1:
            if len(body) > 25: sub = body[0:24]
            else: sub = body
        else: sub = body[0:end_pos]
        sub = sub.replace('\n','')
        sub = sub.replace('\t','')
        sub = sub.replace('  ',' ')
        if msg['Subject'] is None: msg['Subject'] = sub
        else: msg.replace_header('Subject',sub)

    # create same subject list
    ss = []
    for idx, msg in enumerate(mails):
        found_subject = False
        for items in ss:
            #if same_subject(items[0]['Subject'], msg['Subject']):
            if True:
                found_subject = True
                # don't put duplicate emails
                duplicated = False
                for jdx,item in enumerate(items):
                    body = item.get_payload();
                    b2 = msg.get_payload();
                    if len(body)>= len(b2):
                        if body.find(b2) != -1:
                            duplicated = True; break;
                    else :
                        if b2.find(body) != -1:
                            duplicated = True;
                            # replace existing one
                            items[jdx] = msg;
                            break;
                    
                if not duplicated:
                    items.append(msg)
                else: print 'found dup', msg['Subject']
                break
        if not found_subject:
            i = []; i.append(msg);
            ss.append(i)

    print 'diff subjects', len(ss)
    # write to new mbox file
    fout = file('test', 'w')
    for items in ss:
        new_msgs = dedup_chats(items)
        for msg in new_msgs:
            fout.write ('From - \n')
            d = msg['Date']
            s = msg['Sent']
            if d is None and s is None: print 'both None', msg['Subject']
            if s is not None and d is not None: print 'both'
            msgstr = msg.as_string()
            fout.write(msgstr)
            if msgstr[len(msgstr)-1] != '\n':
                fout.write('\n')
    fout.close()
#   print len(mails) 

# compare date for list of emails
def cmp_date(a,b):
    return

if __name__ == '__main__':
    main ()


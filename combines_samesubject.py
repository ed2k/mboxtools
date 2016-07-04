#!/usr/bin/env python
"""  sorted by same subject, remove duplication
"""

import email
from email.MIMEText import MIMEText
import sys, os, string, re

LF = '\x0a'
def remove_re_fw(s):
    while s[:4] in ['RE: ', 'FW: ', 'Re: ', 'Fw: ']:
        s = s[4:]
    return s
 
def same_subject(s1, s2):
    #TODO use sequence matcher to catalog similar subject
    # such as ignore tab, space etc.
    s1 = remove_re_fw(s1)
    s2 = remove_re_fw(s2)
    return s1 == s2

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
        for k, items in enumerate(ss):
            if not same_subject(items[0]['Subject'], msg['Subject']): continue
            found_subject = True
            ss[k].append(msg)
        if not found_subject:
            ss.append([msg])

    nss = []
    for items in ss:
        # sorted by size
        items.sort(key=lambda a:len(a.get_payload()), reverse=True)
        nss.append(items)


    # create same subject list
    ss = nss
    print 'diff subjects', len(ss)
    nss = []
    for items in ss:
        # don't put duplicate emails
        duplicated = False
        nitems = [items[0]]
        
        for item in items[1:]:
            b2 = item.get_payload().strip()
            not_dup = True
            for i in nitems:
                body = i.get_payload()
                if body.find(b2) != -1:
                    not_dup = False
                    print ('found dup', item['Subject'])
                    break         
            if not_dup: nitems.append(item)
        nss.append(nitems)
            
    ss = nss
    print 'diff subjects', len(ss)
    # write to new mbox file
    fout = file('test', 'w')
    for items in ss:
        for msg in items:
            fout.write ('From - \n')
            d = msg['Date']
            s = msg['Sent']
            w = msg['When']
            msgstr = msg.as_string()
            if d is None and s is None and w is None: print ('No_DSW', [msgstr])
            if s is not None and d is not None: print ('both', [msgstr])
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


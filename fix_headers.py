#!/usr/bin/env python
""" fix mail headers
"""

import email
from email.MIMEText import MIMEText
import sys, os, string, re

import mboxlib

LF = '\x0a'

def emails2mbox_file(mails, filename):
    # write to new mbox file
    fout = file(filename, 'w')
    for msg in mails:
        fout.write ('From - \n')
        #str = msg.as_string()
        fout.write(msg)
        if msg[len(msg)-1] != '\n':
                fout.write('\n')
    fout.close()

def fix_header(mailstr):
    checks = mailstr.split('\n\n')
    if len(checks) < 2:
        m = mailstr.replace('=20','');
        m = re.sub(r'\n[ \t]+\n','\n\n',m)
        checks = m.split('\n\n')
        if len(checks) < 2:
            # speical fix, assume '\n> ' seperate the header
            checks = m.split('\n> ')
            header = checks[0]
            body = '\n'.join(checks[1:])
            
    # all kinds of >= 2 case, avoid using goto        
    if len(checks) >= 2:
        if re.match('\n\S+: ', '\n'+checks[1]) is None:
            header = checks[0]
            body = '\n\n'.join(checks[1:])
        else:
            header = checks[0]+'\n'+checks[1]
            body = '\n\n'.join(checks[2:])

    hs = header.splitlines();
    for idx,h in enumerate(hs):
        if re.match('^\S+:\s+', h) is None:
            hs[idx] = ' ' + h
    header = '\n'.join(hs)

    mm = (header+'\n\n'+body);
    return mm

def main ():
    mailboxname_in = sys.argv[1]

    # Open the mailbox.
    mbstr = file(mailboxname_in,'r').read();
    # mbstr = mbstr.replace('\r\n','\n');
    mails = mbstr.split("From - \n");

    # assume no multipart, otherwise run split_attachements first
    nmails = []
    for idx, mail in enumerate(mails):
        #take out the first line
        #i = mail.find("\n");
        if mail.strip() == '': continue
        m =email.message_from_string(mail);
        if m.is_multipart():
            print  "ERROR, split attachment first"
            break
        #if mail[:6] != 'From: ':
        #    mail = 'From: Unknown Person\n'+mail
        nmails.append(mail)
    print 'read in', len(nmails)
    mails = nmails

    # common headers, From, To, Sent, Date, Cc, Subject
    # X-Mozilla-Status, X-Mozilla-Status2, Importance, Received
    # X-Mailer
    m1 = []
    for idx, msg in enumerate(mails):
        mm = mboxlib.fix_column_format2(msg)
        #m2 = mm.split('From: ') 
        #for m in m2[1:]: 
        #    m3 = fix_header('From: '+m)
        mm = mboxlib.fix_header(mm)
        m1.append(mm)


    emails2mbox_file(m1,'test')
    #emails2mbox_file(m2,'t2')
    print ('after ',len(m1)) 

# compare date for list of emails
def cmp_date(a,b):
    return

if __name__ == '__main__':
    main ()


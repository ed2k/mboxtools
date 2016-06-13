#!/usr/bin/env python
""" count mbox formated mails in one file
TODO --seperator format 
auto convert/detect \r\n to \n
"""

import sys, os, string, re

LF = '\x0a'

def main ():
    mailboxname_in = sys.argv[1]
    f_divider = 'From - '

    # Open the mailbox.
    mbstr = open(mailboxname_in,'r').readlines();
    count  = 0
    for line in mbstr:
        line = line.replace('\x0d\x0a','\x0a');
        line = line.replace('\n','')
        if line == f_divider: count += 1
    print(count)
    
    

if __name__ == '__main__':
    main ()


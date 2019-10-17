#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re

def filter_tags(htmlstr):
    blank_line=re.compile('\n+')
    s=blank_line.sub('',htmlstr)
    blank_line_l=re.compile('\n')
    s=blank_line_l.sub('',s)
    blank_kon=re.compile('\t')
    s=blank_kon.sub('',s)
    '''
    blank_one=re.compile('\r\n')
    s=blank_one.sub('',s)
    blank_two=re.compile('\r')
    s=blank_two.sub('',s)
    blank_three=re.compile(' ')
    s=blank_three.sub('',s)
    '''
    return s

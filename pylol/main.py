# encoding: utf-8
import sys

from optparse import OptionParser

from pylol.api import Api

def main():
    '''Module entry point'''

    cmd = sys.argv[1]
    args = sys.argv[2:]

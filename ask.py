#!/usr/local/bin/python

import os, sys, subprocess

def main():
    if len(sys.argv) < 3:
        print 'Usage: ./ask.py <article_text> <N>\n'
        sys.exit(0)

    textfile = sys.argv[1]
    N = sys.argv[2]

    os.chdir('ask')
    subprocess.check_call(['./ask.py', '--txt', textfile,
                            '--N', N])

if __name__ == '__main__':
    main()

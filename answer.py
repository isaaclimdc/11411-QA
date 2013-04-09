#!/usr/local/bin/python

import os, sys, subprocess

def main():
    if len(sys.argv) < 3:
        print 'Usage: ./answer.py <article_text> <questions_text>\n'
        sys.exit(0)

    articletext = sys.argv[1]
    questionstext = sys.argv[2]

    os.chdir('answer')
    subprocess.check_call(['./answer.py', "../" + articletext, "../" + questionstext])

if __name__ == '__main__':
    main()

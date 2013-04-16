#!/afs/andrew.cmu.edu/usr/ysim/python-411/bin/python

import os, sys, subprocess, ntpath

def startREPL(articleFile):
    while True:
        sys.stdout.write("Enter a question: ")
        userQn = sys.stdin.readline()
        tmpFilePath = "tmpQnFile.txt"
        tmpFile = open(tmpFilePath, 'w')
        tmpFile.write(userQn)
        tmpFile.close()

        print("~ Hold on a second while I think...")
        print("~ Here's what I found: ")
        subprocess.check_call(['./answer', articleFile, tmpFilePath])
        print

        subprocess.check_call(['rm', tmpFilePath])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: ./robot.py <article_text>\n'
        sys.exit(1)

    articleFile = sys.argv[1]
    baseFile = ntpath.basename(articleFile)
    print("Question Answerer (" + baseFile + ")")
    print("-----------------\n")

    startREPL(articleFile)

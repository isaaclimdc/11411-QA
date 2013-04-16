#!/afs/andrew.cmu.edu/usr/ysim/python-411/bin/python

import os, sys, subprocess, contextlib

@contextlib.contextmanager
def nostderr():
    savestderr = sys.stderr
    class Devnull(object):
        def write(self, _): pass
    sys.stderr = Devnull()
    yield
    sys.stderr = savestderr

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: ./answerrepl.py <article_text>\n'
        sys.exit(1)

    articleFile = sys.argv[1]

    while True:
        print "Enter a question: "
        userQn = sys.stdin.readline()
        tmpFile = open("tmpQnFile", 'w')
        tmpFile.write(userQn)
        tmpFile.close()

        # with nostderr():
        output_f = open('tmpAnsFile.txt', 'w')
        subprocess.Popen(['./answer', articleFile, tmpFile], stdout=output_f)
        output_f.close()

        tmpAnsFile = open("tmpAnsFile.txt")
        tmpAns = tmpAnsFile.read()
        print tmpAns
        tmpAnsFile.close()


11-411 Question and Answer
========

Team "sudo rm -rf /"
--------------------
- Manish Burman
- Shannon Joyner
- Isaac Lim

Requirements
------------
This was tested on `ghc20.ghc.andrew.cmu.edu`. All commands below are executed in the root
level of the project directory. This project requires:

- Python 2.7
- Python NLTK (to get this first make sure nltk is installed. Then go into a python shell and type `import nltk` then `nltk.download()`, and install everything there.)
- Java
- Stanford CoreNLP Package
- NodeBox Linguistics Package

All the above dependencies can be installed by simply running `./dep.sh` at the root of the project directory. The dependencies will be downloaded and installed into the `libraries` directory.

Ask
---
`./ask <article.txt> <N>`

This will generate `N` questions from a given `article.txt`. Redirecting (`>`) the output will send ONLY the questions to a file.

Answer
------
`./answer <article.txt> <questions.txt>`

This will answer the questions in `questions.txt` (1 per line), looking for the answers in `article.txt`. Redirecting (`>`) the output will send ONLY the answers to a file.

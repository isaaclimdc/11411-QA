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

- Python
- Java
- Stanford CoreNLP Package
- NodeBox Linguistics Package

All the above dependencies can be installed by simply running `./dep.sh` at the root of the project directory. The dependencies will be downloaded and installed into the `libraries` directory.

Also

a) We require python 2.7
b) We require pythons nltk toolkit
To get this first make sure nltk is installed 
Then go into a python shell and type
>>> import nltk
>>> nltk.download()
  Install everything

Ask
---
`./ask.py <article.txt> <N>`

This will generate `N` questions from a given `article.txt`.

Answer
------
`./answer.py <article.txt> <questions.txt>`

This will answer the questions in `questions.txt` (1 per line), looking for the answers in `article.txt`.

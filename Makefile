#
# Makefile for ./ask and ./answer
#

CC = gcc
CFLAGS = -Wall -Wextra -Werror -g -std=c99

all: ask.c answer.c
	$(CC) $(CFLAGS) ask.c -o ask
	$(CC) $(CFLAGS) answer.c -o answer

clean:
	rm -rf ask answer ask.dSYM answer.dSYM
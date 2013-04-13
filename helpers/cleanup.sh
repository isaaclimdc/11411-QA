#!/bin/sh

echoerr() { echo "$@" 1>&2; }

echoerr '~ Cleaning up tmp files...'
rm -rf tmp
echoerr '~ DONE!\n'
#!/bin/bash

#set -xv

echo "Remember to save the file (Ctrl+S) before compiling!"

rm bin -r > /dev/null 2>&1
rm *.class > /dev/null 2>&1

javac *.java
make test > /dev/null

rm bin -r > /dev/null 2>&1
rm *.class > /dev/null 2>&1

echo "Done."
exit 0




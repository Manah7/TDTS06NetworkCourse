#!/bin/bash

if test $# -ne 1
then
	echo "One argument expected : source file."
	exit 1
elif test ! -f $1
then
	echo "The specified file doesn't exist."
	exit 1
fi

echo "Starting building..."
g++ -Wall -Wextra -Wpedantic -std=c++17 $1 -o $1.out

if test $? -eq 0
then
	echo "Build finished. Running..."
	echo ""
	./$1.out
	echo ""
	echo "Done. Cleaning..."
	rm $1.out
	echo "Done."
else
	echo "Build failed."
fi

exit 0

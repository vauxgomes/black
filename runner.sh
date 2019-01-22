#!/bin/bash

# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com

# Reference
# ---------
# [1] Loïc Cerf, Jérémy Besson, Céline Robardet,
# and Jean-François Boulicaut. Data-Peeler: Constraint-Based
# Closed Pattern Mining in n-ary Relations.
# 
# [2] Loïc Cerf and Wagner Meira Jr. Complete
# Discovery of High-Quality Patterns in Large
# Numerical Tensors. 
# 
# [3] Takeaki Uno, Masashi Kiyomi, Hiroki Arimura,
# LCM ver.3: Collaboration of Array, Bitmap and
# Prefix Tree for Frequent Itemset Mining

# Usage Info 
function show_help {
	echo -e "\033[1mBoostlac Main Script\033[0m"

cat << EOF
Version: 0.1

Usage: [-hemZADCS] [-s FILES] [-t FILES] [-b NUM] [-p ARGS]
Arguments:
 -h 	Displays help
 -s 	Training Files (Required)
 -t 	Testing files (Required)
 -z 	MINER:   Minimum support size (default: 1)
 -m 	MINER:   Use Multidupehack to mine the itemsets (default: D-peeler)
 -l 	MINER:   Use LCM to mine the itemsets (default: D-peeler)
 -e 	BOOSTER: Activates Eager Mode
 -Z 	BOOSTER: Deactivates ZERO classifier
 -A 	BOOSTER: Deactivates Associative Classifier
 -D 	BOOSTER: Activates Discrete Adaboost 
 -C 	BOOSTER: Activates Confidence-rated Adaboost
 -S 	BOOSTER: Activates SLIPPER Boost
 -c 	BOOSTER: Activates Internal Cross Validation
 -o 	BOOSTER: Activates use of original train size
 -j 	BOOSTER: Activates use of Jaccard\'s index
 -b 	BOOSTER: Maximum number of rounds
 -f 	BOOSTER: Uses only free itemsets

NOTE: This code works only for luccskdd files.
EOF

	exit
}

# Easy color print function
function cerr {
	echo -e "\033[95m$1\033[0m" 1>&2
}

# Header of the files
function header {
	echo -n "# Mode: "
	if $3; then echo "Eager"
	else echo "Lazy"; fi

	echo -n "# Miner: "
	if $4; then echo "Multidupehack"
	elif $5; then echo "Lcm"
	else echo "D-peeler"; fi

	echo "# Train:" ${1##*/}
	echo "# Test:" ${2##*/}

	echo "#"
	echo "# Date:" `date`
	echo "# Host:" `hostname`

	echo ""
}

# Safety
if [ -z "$1" ]; then show_help; fi

# Pre-set variables
e=false # Eager mode (false = Lazy)
m=false # Multidupehack switch (false = D-peeler)
l=false # LCM switch (false = D-peeler)

Z=true # ZERO classifier
A=true # Associative classifier {LAC, EAC}
D=false # Discrete Adaboost
C=false # Conf-rated Adaboost
S=false # SLIPPER

c=false
o=false # Sizes
j=false # Jaccard's index
f=false # Free itemsets

# Minimum support size for D-peeler / Multidupehack
MSIZE=1

# Parsing options
while getopts ":hs:t:z:mleZADCScojb:f" opt
do
	case $opt in
	h) show_help ;;
	s)
		OPTARG="$(ls $OPTARG)" # POG
		for file in $OPTARG
		do
			TRAIN+=($file)
		done ;;
	t)
		OPTARG="$(ls $OPTARG)" # POG
		for file in $OPTARG
		do
			TEST+=($file)
		done ;;
	z) MSIZE=$OPTARG ;;
	m) m=true ;;
	l) l=true ;;
	e) e=true ;;
	Z) Z=false ;;
	A) A=false ;;
	D) D=true ;;
	C) C=true ;;	
	S) S=true ;;
	c) c=true ;;
	o) o=true ;;
	j) j=true ;;
	b) b=$OPTARG ;;
	f) f=true ;;
	
	:)
		cerr "Option -$OPTARG requires an argument." >&2
		exit 1
		;;
	\?)
		cerr "Invalid option: -$OPTARG" >&2
		exit 1
		;;
	esac
done

# Safety: Checking presence of arrays
if [ ${#TRAIN[@]} -eq 0 ]
then
	cerr "Required option: -s"	
	exit 1
elif [ ${#TEST[@]} -eq 0 ]
then
	cerr "Required option: -t"
	exit 1
fi

# Safety: Checking size equality of arrays
if [ ${#TRAIN[@]} -ne ${#TEST[@]} ]
then 
	cerr "Sizes of Train and Test arrays are uneven"
	exit 1
fi

# Building boosting initial options
if $Z || $A || $D || $C || $S
then
	BOPTIONS="-"
	if $Z; then BOPTIONS+="Z"; fi
	if $A; then BOPTIONS+="A"; fi
	if $D; then BOPTIONS+="D"; fi
	if $C; then BOPTIONS+="C"; fi
	if $S; then BOPTIONS+="S"; fi
fi

# Internal Cross Validation
if $c; then BOPTIONS+="c"; fi

# Rounds
if [ -n "$b" ]; then BOPTIONS+=" -b $b";fi

# Free itemsets
if $f; then BOPTIONS+=" --free";fi

#
TMP=`mktemp -t runner.sh.XXXXXX`
trap "rm $TMP* 2>/dev/null" 0

# Jaccard's index
if $j; then
	BOPTIONS+=" -j $TMP.jc"; 
	jaccard="use jaccard" # Just an unempty string
fi

# Variable for awk projection, if necessary
if $m; then form="use multidupehack"; fi # Just an unempty string

# Learning Stage
length=${#TRAIN[@]}
for ((i = 0; i < length; i++))
do
	# Printing header
	header ${TRAIN[i]} ${TEST[i]} $e $m $l

	# Eager Mode
	if $e
	then
		# Creating class files
		awk -v prefix=$TMP '{print NR >> prefix ".class." $NF}' ${TRAIN[i]}

		# Preparing train file + Running miner + Calling booster
		if $m
		then
			# multidupehack
			awk 'BEGIN { OFS = "," } { --NF; print NR " " $0 " " 1 }' ${TRAIN[i]} | \
			multidupehack -u 1 -s "$MSIZE 0" /dev/stdin -o /dev/stdout | \
			./boost/main.py -s $TMP.class* -t ${TEST[i]} -i /dev/stdin $BOPTIONS || break
		elif $l
		then
			# lcm
			awk 'BEGIN { OFS = "," } { --NF; print NR " " $0 }' ${TRAIN[i]} | \
			lcm IF_ ${TRAIN[i]} 1 - 2> /dev/null 
		else
			# d-peeler
			awk 'BEGIN { OFS = "," } { --NF; print NR " " $0 }' ${TRAIN[i]} | \
			d-peeler -s "$MSIZE 0" /dev/stdin -o /dev/stdout | \
			./boost/main.py -s $TMP.class* -t ${TEST[i]} -i /dev/stdin $BOPTIONS || break
		fi

		# Deleting remanescent files
		rm $TMP*
	# Lazy Mode 
	else
		# Train sizes
		if $o; then
			SIZES=`mktemp -t runner.sh.XXXXXX`
			trap "rm $SIZE 2>/dev/null" 0

			awk '{++size[$NF]}END{for (i in size) { print i, size[i]}}' ${TRAIN[i]} > $SIZES
			BOPTIONS+=" -o $SIZES"
		fi
		
		row=0 # Row for deletion
		while read -r example
		do
			# Row for deletion from projection
			row=$((row + 1))

			# Wrinting the test file
			echo $example > $TMP.testset

			# Features to project
			fts=`expr "$example" : '\(.*\) .*'`

			# Preparing projected train + Creating the class files
			sed $((row))d ${TRAIN[i]} | awk -v prefix=$TMP -v object="$fts" -v form="$form" -v jaccard="$jaccard" '
			BEGIN {
				n = split(object, tmp);
				for (i = 1; i <= n; ++i)
					attributes[tmp[i]] = ""
			}{
				empty = "t";
				intersection = 0

				#
				for (i = 1; i != NF; ++i) {
					if ($i in attributes) {
						if (empty == "")
							printf "," $i >> prefix;
						else {
							empty = "";
							printf NR " " $i >> prefix
						}

						intersection++
					}
				};

				if (empty == "") {
					# For multidupehack
					if (form) { 
						# If FORM is a non-empty string AWK understands it as true value
						# And so it prints the projection in the multidupehack format

						print " 1" >> prefix;
		                print "0 " NR >> prefix ".class." $NF

		            # For d-peeler
					} else {
						print "" >> prefix;
						print NR >> prefix ".class." $NF
					}

					# Jaccard
					if (jaccard) {
						union = n + NF - intersection - 1 # Class counts in NF
						print NR " " intersection/union >> prefix ".jc"
					}

				}
			}'

			# Safety: Avoiding empty projection
			if [ ! -s $TMP ]; then continue; fi

			# Running Miner and + Calling booster
			if $m
			then
				# multidupehack
				multidupehack -s '$MSIZE 0' -u 1 -o /dev/stdout $TMP | \
				./boost/main.py -s $TMP.class* -t $TMP.testset -i /dev/stdin $BOPTIONS || break
			elif $l
			then
				# lcm
				cut -f 2 -d " " $TMP > $TMP.lcm; lcm IC_ $TMP.lcm 0 - 2> /dev/null | \
				./boost/main.py -s $TMP.class* -t $TMP.testset -i /dev/stdin $BOPTIONS --rmode lcm || break
			else
				# d-peeler
				d-peeler -s "$MSIZE 0" -o /dev/stdout $TMP 2> /dev/null | \
				./boost/main.py -s $TMP.class* -t $TMP.testset -i /dev/stdin $BOPTIONS || break
			fi

			# Deleting remanescent files
			rm $TMP*
			# exit 1
		done < ${TEST[i]}
	fi

	# Printing footer
	echo ""
done
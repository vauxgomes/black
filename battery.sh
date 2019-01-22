#!/bin/bash

# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com

# Usage Info
function show_help {
	echo -e "\033[1mBoostlac Battery Script\033[0m"

	cat << EOF
Version: 0.1

Usage: $0 [-hn] [-x ARG] -m "ARGS" [-B NUM] [-s NUM] [-e NUM] [-p PATH] [-l LOG]
Arguments:
 -h 	Displays help
 -x 	Files extension name (default: randomly assigned)
 -m 	MINER: miner options occordingly with runner script*
 -B 	Battery dataset package (default: 0, values: 0 ~ 4)
 -s 	Fold start (default: 1)
 -e 	Fold end (default: 10)
 -p 	Path for result outputs (default: ./results)
 -l 	Progress / history file (default: .batt)
 -n 	Show notifications (default: false)

* Required
EOF

	exit
}

# Moving LOG easily
function mlog {
	if [ ! -d $logdir ]
	then
		mkdir $logdir
		echo -e "\033[96m ~Created $logdir directory\033[0m"
	fi

    if [ -f $logfile ]
	then
        mv $logfile logs/$1
        echo -e " \033[94m ~$logfile moved to $logdir/$1\033[0m"
    fi
}

# Formatted data
function cdata {
	date +"%b %d %H:%M:%S"
}

# Easy color print function
function cerr {
	echo -e "\033[95m$1\033[0m" 1>&2
}

# Notification function
function notifyme {
	notify-send -u critical "$1" "$2"
}

# Safety: First check on arguments
if [ -z "$1" ]; then show_help; fi

# Pre-set variables
n=false # Notification flag
output=.batt
bpack=0

# Folds
begin=1
end=10

# Variables
resdir=results
logdir=logs
logfile=log.json

# Parsing options
while getopts ":hnB:x:m:s:e:p:l:" opt
do
	case $opt in
	h) show_help ;;
	x) ext=$OPTARG ;;
	B) bpack=$OPTARG ;;
	m) moptions=$OPTARG ;;
	s) begin=$OPTARG ;;
	e) end=$OPTARG ;;
	p) resdir=$OPTARG ;;
	l) output=$OPTARG ;;
	n) n=true ;;
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

# Safety: Checking the presence of some arguments
if [ -z "$moptions" ]
then
	cerr "Required option: -m"
	exit 1
fi

# Choosing ext randomly
if [ -z $ext ]
then
	ext=`mktemp -u -t XXXXXXX`
	ext=`basename $ext`
	cerr "-x was randomly assigned to: $ext"
fi

# Safety: Creating results directory
if [ ! -d $resdir ]
then
	mkdir $resdir
	echo -e "\033[96m Created $resdir directory\033[0m"
fi

# Safety: Removing possible reminiscent LOG
if [ -a $logfile ]; then rm $logfile; fi

# Dataset packages
case $bpack in
	0) array=(labor postoperative iris tae haberman flare zoo glass) ;;
	1) array=(ecoli liver heart-h wine balance heart-statlog lymphography breast) ;;
	2) array=(heart-c tictactoe car autos anneal hepatitis cmc) ;;
	3) array=(diabetes credit-a colic australian crx vehicle dermatology primary-tumor credit-g) ;;
	4) array=(vote hypothyroid segment sick mushroom pendigits letter) ;;
	5) array=(banknote climate-model dow-jones hayes-roth mammographic-mass meta teaching-assistant) ;;
	6) array=(user-knowledge monks contraceptive blood wholesale) ;;
	7) array=(messidor student-math) ;;
	*) array=(labor postoperative iris tae haberman flare zoo glass ecoli liver heart-h \
		wine balance heart-statlog lymphography breast heart-c tictactoe car autos anneal \
		hepatitis cmc diabetes credit-a colic australian crx vehicle dermatology \
		primary-tumor credit-g vote hypothyroid segment sick mushroom pendigits letter) ;;
esac

# Header
echo "--"
echo -e "\033[1mBATTERY\033[0m"
echo " Miner: $moptions"
echo " Folds: $begin~$end"
echo " Pack: $bpack"
echo " --"
echo " Log: $output"
echo -e " Ext: .$ext \n"
echo -ne " \033[1mStarted:\033[0m `cdata`\n"

# Header history file
echo -e "--\nBATTERY\n Started: `cdata`\n" >> $output

# Auxiliary variables
counter=1
total=${#array[@]}
step=$((100 / total))
progress=$step

# Battery
for data in ${array[@]}
do
	filename=$data.$ext # Dataset output name
	result=$resdir/$filename # Dataset output path

	# Safety
	if [ -a $result ]; then rm $result; fi

	# Started
	echo -n "  - $filename"
	echo -e " $filename\n ------------------------" >> $output
	
	# Folds
	for ((k = begin; k <= end; k++))
	do
		# Fold name
		if [ $k -lt 10 ]; then
			fname=0$k
		else
			fname=$k
		fi

		# Running miner
		./runner.sh -s ~/Projects/data/$data*/*train*$k -t ~/Projects/data/$data*/*test*$k $moptions > $result-$fname

		# Tracking progress
		printf " %s %3s %s \n" "Fold" "$k:" "`cdata`" >> $output
	done
	
	# Finished 
	echo -e "\r  \033[1m$progress%\033[0m $filename"
	echo -e " -------------------- $progress%\n" >> $output

	# Notify me
	if $n; then notifyme "$filename" "Done: $progress%"; fi
	
	#
	progress=$((progress + step))
	counter=$((counter + 1))

	# Log 
	mlog $data.$ext$2.json
done

# Footer
echo -e " \033[1mFinished:\033[0m `cdata`\n--"
echo -e " Finished: `cdata`\n--\n" >> $output

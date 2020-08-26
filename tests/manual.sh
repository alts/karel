#!/bin/zsh

CLEAR='\033[0m'

RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
PURPLE='\033[35m'
CYAN='\033[36m'
FAINT='\033[2m'

cd "$(dirname "$(realpath "$0")")";

LOGFILE="./manual.log"

pip install -U ..
karel=`which karel`

date >> $LOGFILE

tested() {
    local opt=$1
    # to expand array: ${(P)${opt}}
    echo "${YELLOW}Try $2${CLEAR}"
    echo karel ${(P)${opt}}
    echo -en "${FAINT}Press any key to continue.${CLEAR}" 
    read -s -k "? "
    echo
    $karel ${(P)${opt}}
    echo -en "${FAINT}Press Y/y if it worked OK:${CLEAR}"
    if read -k -q "choice? "; then
        echo -n "OK" >> $LOGFILE
    else
        echo -n "FAIL" >> $LOGFILE
    fi
    echo -e "\t$2:\n\t$1" >> $LOGFILE 
    echo
}


OPT=()                 tested OPT "running karel executable"
OPT=(-XY)              tested OPT "infinite parameters"
OPT=(-x 1)             tested OPT "one line X"
OPT=(-y 1) 	       tested OPT "one line Y"
OPT=(-x 2 -y 2)        tested OPT "small world"
OPT=(-k 1 1)           tested OPT "set position"
OPT=(-x 2 -y 2 -k 1 1) tested OPT "small world set position"
OPT=(-b 0) 	       tested OPT "no beepers"
OPT=(-b 2) 	       tested OPT "2 beepers"
OPT=(-s 1) 	       tested OPT "speed 1 tick/s"
OPT=(-q) 	       tested OPT "quiet mode"
OPT=(-v)               tested OPT "verbose mode"
OPT=(-L 2) 	       tested OPT "lookahead 2"
OPT=(-o manual.km2)    tested OPT "saving file"

P_TREASURE="../programs/graph/3_treasure.ks"
M_TREASURE="../world/maze/treasure/07.km2"

OPT=(-s 60 -p $P_TREASURE -m $M_TREASURE) tested OPT "graph"


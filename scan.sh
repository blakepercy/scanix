#!/bin/bash
set +e

HELP=false
VERB=false

while [[ $# > 0 ]]
do
	key="$1"

	case $key in
		-l|--local)
		LOCAL="$2"
		shift
		;;
		-f|--file)
		FILE="$2"
		shift
		;;
		-h|--help)
		HELP=true
		shift # past argument
		;;
		-v|--verbose)
		VERB=true
		shift
		;;
		--default)
		DEFAULT=YES
		;;
		*)
			   # unknown option
		;;
	esac
	shift # past argument or value
done

if $VERB; then
    echo LOCAL  = "${LOCAL}"
    echo FILE  = "${FILE}"
fi

if $HELP; then
    echo ""
    echo -e "scan - start scanning local or remote log files and alarm for given keywords"
    echo -e "  Usage: ./scan.sh OR scan.sh -l \"name of system\" -f \"file to scan\""
    echo ""
else
	if [[ -n $LOCAL ]]; then
		setalarm -l $LOCAL -f $FILE -s ~/scanix/etc/setalarm/systems.conf -k ~/scanix/etc/setalarm/keywords.conf -x ~/scanix/etc/setalarm/keywords-exclude.conf
	else
		setalarm -s ~/scanix/etc/setalarm/systems.conf -k ~/scanix/etc/setalarm/keywords.conf -x ~/scanix/etc/setalarm/keywords-exclude.conf
	fi
fi

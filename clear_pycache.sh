to_rm=$(find -type d | grep __pycache__$)
if [ -z "$to_rm" ]
then
	echo "Nothing to remove"
else
	echo "Removing"
	echo $to_rm
	rm -r $to_rm
fi

#this script is used to check for the existence of a file
while true; do
if [ -r $1 ]; then
        exit 0
fi

sleep 2

done

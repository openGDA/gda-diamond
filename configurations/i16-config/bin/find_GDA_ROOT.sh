# Using $GDA_ROOT as a starting point, walks up the directory tree until it
# finds a "plugins" folder, which it assumes to be the GDA root directory.

# Check we have a starting value
if [ -z "$GDA_ROOT" ]; then
  echo "\$GDA_ROOT is not set. Giving up".
  exit 1
fi

# Walk up the directory tree until a "plugins" directory is found
while [ ! -d $GDA_ROOT/plugins ]
do
  if [ "$GDA_ROOT" == "/" ]; then
    echo "Couldn't find GDA root. Giving up."
    exit 1
  fi
  GDA_ROOT=`dirname $GDA_ROOT`
done

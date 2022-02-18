#!/bin/sh

rm -rf build/

# prepare the env variables
FILENAME=$(basename node/activeeon_enterprise-node-linux-x64-*.zip)

export VERSION=$(python -c "version_string = \"$FILENAME\"[:-4]; version = version_string.split(\"-\")[4:]; print \"-\".join(version)")

export NODE=$(readlink -f node/)

# create the deb packages
./packaging/build-packages.sh deb

# create the rpm packages
docker build -t agent-linux-packaging-centos packaging/rpm/

chmod -R o+rw $(pwd) # so packager user in container can read and write in the volume
docker run -v $(pwd):/repo -v $NODE:/node -e NODE=/node -e VERSION=$VERSION -t --rm agent-linux-packaging-centos /repo/packaging/build-packages.sh rpm

# rm -rf node/
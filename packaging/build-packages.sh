#!/bin/bash

set -e

VENDOR="activeeon-dev@activeeon.com"
DESCRIPTION="The ProActive Agent enables desktop computers as an important source of computational power"
URL="http://activeeon.com"

VERSION=${VERSION:-1.0.3}

[ -n "$NODE" ] || ( echo "NODE variable should point to a directory with activeeon_enterprise-node archives"; exit 1 )

THIS=$(cd $(dirname $0); pwd)
REPO=$(dirname $THIS)
BUILD=$REPO/build/

export GEM_HOME=~/gems

KIND=$1
[ -n "$KIND" ] || ( echo "usage: $0 <deb|rpm>"; exit 1 )

install_fpm () {
    [ -f "$GEM_HOME/bin/fpm" ] || gem install fpm -f -V --no-user-install --bindir $GEM_HOME/bin
}

package () {
    local KIND=$1
    local ARCH=$2
    [ -n "$KIND" ] || ( echo "usage: package <deb|rpm> <i386|amd64>"; exit 1 )
    [ -n "$ARCH" ] || ( echo "usage: package <deb|rpm> <i386|amd64>"; exit 1 )

    local PREFIX=$BUILD/$KIND/$ARCH

    rm -fr $PREFIX

    mkdir -p $PREFIX/etc/init.d
    cp $REPO/packaging/$KIND/proactive-agent $PREFIX/etc/init.d

    mkdir -p $PREFIX/opt/proactive-agent
    rsync -avP --delete $REPO/proactive-agent $REPO/proactive-agent.1 $REPO/palinagent $REPO/config* $REPO/data $REPO/LICENSE.txt \
        $PREFIX/opt/proactive-agent/

    case $ARCH in
        amd64)
            local NODE_PACKAGE=$NODE/activeeon_enterprise-node-linux-x64-*.zip
            ;;
        i386)
            local NODE_PACKAGE=$NODE/activeeon_enterprise-node-linux-i586-*.zip
    esac

    (cd $PREFIX/opt; unzip $NODE_PACKAGE; mv activeeon_enterprise-node* proactive-node)

    mkdir -p $BUILD/distributions
    ~/gems/bin/fpm -s dir -t $KIND -C $PREFIX -p $BUILD/distributions/ \
        -n "proactive-agent" \
        -v $VERSION \
        -a $ARCH \
        --maintainer "$VENDOR" \
        --vendor "$VENDOR" \
        --description "$DESCRIPTION" \
        --url "$URL" \
        -d python -d python-lxml \
        --post-install $REPO/packaging/$KIND/postinst  \
        --pre-uninstall $REPO/packaging/$KIND/prerm \
        --post-uninstall $REPO/packaging/$KIND/postrm \
        .
}

install_fpm

for ARCH in amd64 i386; do
    package $KIND $ARCH
done


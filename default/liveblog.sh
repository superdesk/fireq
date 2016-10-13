#!/bin/sh
set -xe

root=$(dirname $(dirname $(realpath -s $0)))

. $root/common/index.sh
install

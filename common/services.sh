#!/bin/sh
set -e

root=$(dirname $(dirname $(realpath -s $0)))
. $root/common/index.sh

do_services

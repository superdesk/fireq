{{>init/lb.sh}}

cat <<EOF >> {{config}}
SYNDICATION=true
EOF

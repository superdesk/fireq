{{>init/sd.sh}}

{{>init/.amazon.sh}}

cat <<EOF >> {{config}}
MAIL_SERVER=10.0.3.1

{{>init/.amazon.sh}}
MEDIA_PREFIX=https://$AMAZON_CONTAINER_NAME.s3-$AMAZON_REGION.amazonaws.com/$AMAZON_S3_SUBFOLDER
EOF

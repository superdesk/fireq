_missing_db() {
    curl -sI $ELASTICSEARCH_URL/$CONTENTAPI_ELASTICSEARCH_INDEX | grep -q 404
}

_activate

if _missing_db; then
  curl -s -XPUT $ELASTICSEARCH_URL/$CONTENTAPI_ELASTICSEARCH_INDEX
  cd {{repo}}
  set +e
  python manage.py create_user admin@example.com admin Admin Admin true;
  set -e
fi

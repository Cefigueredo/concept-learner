#!/usr/bin/env bash
psql=( psql -v ON_ERROR_STOP=1 --dbname "$POSTGRES_DB" --username "$POSTGRES_USER")

find /docker-entrypoint-initdb.d -mindepth 2 -type f -print0 | sort -z | while read -d $'\0' f; do
  case "$f" in
    *.sh)
      if [ -x "$f" ]; then
        echo "$0: running $f"
        "$f"
      else
        echo "$0: sourcing $f"
        . "$f"
      fi
      ;;
    *.sql)    echo "$0: running $f"; "${psql[@]}" -f "$f"; echo ;;
    *.sql.gz) echo "$0: running $f"; gunzip -c "$f" | "${psql[@]}"; echo ;;
    *)        echo "$0: ignoring $f" ;;
  esac
  echo
done

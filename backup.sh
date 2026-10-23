#!/bin/bash
set -euo pipefail

BACKUP_DIR=/mnt/backups
DATE=$(date +%Y%m%d_%H%M%S)
FILE="$BACKUP_DIR/finance_$DATE.sql.gz"

# Sauvegarde dans un fichier temporaire, renommé seulement si tout a réussi
docker exec postgres pg_dump -U finance_user financedb | gzip > "$FILE.tmp"
mv "$FILE.tmp" "$FILE"

# Supprime les sauvegardes de plus de 30 jours
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'finance_*.sql.gz' -mtime +30 -delete

echo "Backup terminé : $FILE"

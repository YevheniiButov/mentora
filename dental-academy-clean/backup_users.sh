#!/bin/bash
# Backup script for existing users before migration

echo "🛡️ Creating backup of existing users..."

# Create backup directory
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

# Backup users table
echo "📊 Backing up users table..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -t "user" > $BACKUP_DIR/users_backup.sql

# Backup specific user data
echo "👥 Backing up user data..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
COPY (
    SELECT id, email, username, first_name, last_name, role, is_active, created_at
    FROM "user"
) TO '$BACKUP_DIR/user_data.csv' WITH CSV HEADER;
"

echo "✅ Backup completed in $BACKUP_DIR"
echo "📁 Files created:"
echo "   - users_backup.sql (full table)"
echo "   - user_data.csv (user data)"

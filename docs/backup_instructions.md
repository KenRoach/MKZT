# Database and Metabase Backup System

This document provides instructions on how to use the backup system for the MKZT application and Metabase analytics platform.

## Overview

The backup system consists of:

1. **Automated daily backups** - Scheduled to run at 2 AM every day
   - PostgreSQL database backup
   - Metabase configuration and data backup
2. **Manual backup capability** - For on-demand backups
3. **Restore functionality** - To restore both database and Metabase from backups

## Backup Storage

Backups are stored in the `./backups` directory and are automatically compressed:
- Database backups: `mkzt_backup_YYYYMMDD_HHMMSS.sql.gz`
- Metabase backups: `metabase_backup_YYYYMMDD_HHMMSS.tar.gz`

The system retains backups for 7 days by default, after which older backups are automatically deleted.

## Using the Backup System

### Starting the Services

The backup service and Metabase are included in the Docker Compose configuration. To start them:

```bash
docker-compose up -d
```

This will start:
- The backup service (scheduled daily backups at 2 AM)
- Metabase analytics platform (accessible at http://localhost:3000)
- Other application services

### Setting Up Metabase

To set up Metabase with initial dashboards:

```bash
./scripts/setup_metabase.sh
```

This will create:
- Orders Overview Dashboard
- Customer Analytics Dashboard
- Merchant Performance Dashboard
- Driver Analytics Dashboard

### Manual Backup

To perform a manual backup of both database and Metabase:

```bash
./scripts/manual_backup.sh
```

This will create backups immediately and display information about the backup files.

### Restoring from Backups

To restore the database:
```bash
./scripts/restore_database.sh <backup_file>
```

Example:
```bash
./scripts/restore_database.sh ./backups/mkzt_backup_20230101_120000.sql.gz
```

To restore Metabase:
```bash
./scripts/restore_metabase.sh <backup_file>
```

Example:
```bash
./scripts/restore_metabase.sh ./backups/metabase_backup_20230101_120000.tar.gz
```

**Warning**: Restoring from a backup will overwrite the current data. Make sure to back up any important data before performing a restore.

## Backup Configuration

### Changing Backup Schedule

To change the backup schedule, edit the cron expression in the `docker-compose.yml` file:

```yaml
echo '0 2 * * * /scripts/backup_database.sh >> /var/log/cron.log 2>&1' > /etc/cron.d/backup-cron
```

The format is: `minute hour day_of_month month day_of_week command`

### Changing Retention Period

To change how long backups are retained, edit the `RETENTION_DAYS` variable in `scripts/backup_database.sh`:

```bash
RETENTION_DAYS=7
```

## Metabase Configuration

### Default Access

- URL: http://localhost:3000
- Default admin credentials: admin@metabase.local / admin
- Change these credentials after first login!

### Email Configuration

Metabase email settings can be configured in the `docker-compose.yml` file:

```yaml
environment:
  - MB_EMAIL_SMTP_HOST=${SMTP_SERVER}
  - MB_EMAIL_SMTP_PORT=${SMTP_PORT}
  - MB_EMAIL_SMTP_USERNAME=${SMTP_USERNAME}
  - MB_EMAIL_SMTP_PASSWORD=${SMTP_PASSWORD}
  - MB_EMAIL_FROM=${FROM_EMAIL}
```

## Troubleshooting

### Backup Logs

Backup logs are stored in `/var/log/cron.log` inside the backup container. To view the logs:

```bash
docker-compose exec backup cat /var/log/cron.log
```

### Common Issues

1. **Backup fails due to insufficient disk space**
   - Clean up old backups manually: `find ./backups -name "*.gz" -type f -delete`
   - Increase disk space allocation

2. **Restore fails due to incompatible backup format**
   - Ensure you're using a backup created by the same version of pg_dump/Metabase
   - Check if the backup file is corrupted

3. **Backup service not running**
   - Restart the backup service: `docker-compose restart backup`
   - Check the logs: `docker-compose logs backup`

4. **Metabase issues**
   - Check Metabase logs: `docker-compose logs metabase`
   - Restart Metabase: `docker-compose restart metabase`
   - Clear browser cache and try again 
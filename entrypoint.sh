#!/bin/bash
set -e

echo "=== FusionPBX Container Starting ==="

# Create necessary directories
mkdir -p /var/run/php
mkdir -p /var/log/supervisor
mkdir -p /var/log/nginx
mkdir -p /var/log/fusionpbx

# Set permissions
chown -R www-data:www-data /var/www/fusionpbx
chmod -R 755 /var/www/fusionpbx

# Create FusionPBX config directory if not exists
if [ ! -d "/etc/fusionpbx" ]; then
    mkdir -p /etc/fusionpbx
    chown -R www-data:www-data /etc/fusionpbx
fi

# Wait for PostgreSQL if DATABASE_HOST is set
if [ -n "$DATABASE_HOST" ]; then
    echo "Waiting for PostgreSQL at $DATABASE_HOST:${DATABASE_PORT:-5432}..."
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if pg_isready -h "$DATABASE_HOST" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USERNAME:-fusionpbx}" > /dev/null 2>&1; then
            echo "PostgreSQL is ready!"
            break
        fi
        
        attempt=$((attempt + 1))
        echo "Waiting for PostgreSQL... attempt $attempt/$max_attempts"
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo "Warning: Could not connect to PostgreSQL, continuing anyway..."
    fi
fi

# Generate FusionPBX config.php if it doesn't exist
CONFIG_FILE="/etc/fusionpbx/config.php"
if [ ! -f "$CONFIG_FILE" ] && [ -n "$DATABASE_HOST" ]; then
    echo "Creating FusionPBX config.php..."
    cat > "$CONFIG_FILE" << CONFIGEOF
<?php
// FusionPBX Database Configuration
\$db_type = 'pgsql';
\$db_host = '${DATABASE_HOST}';
\$db_port = '${DATABASE_PORT:-5432}';
\$db_name = '${DATABASE_NAME:-fusionpbx}';
\$db_username = '${DATABASE_USERNAME:-fusionpbx}';
\$db_password = '${DATABASE_PASSWORD}';
\$db_path = '';
\$db_secure = false;
\$db_cert_authority = '';

// FreeSWITCH Event Socket
\$event_socket_ip_address = '${EVENT_SOCKET_HOST:-127.0.0.1}';
\$event_socket_port = '${EVENT_SOCKET_PORT:-8021}';
\$event_socket_password = '${EVENT_SOCKET_PASSWORD:-ClueCon}';

// Project paths
\$document_root = '/var/www/fusionpbx';
?>
CONFIGEOF
    chown www-data:www-data "$CONFIG_FILE"
    chmod 640 "$CONFIG_FILE"
    echo "Config file created at $CONFIG_FILE"
fi

# Create symlink if config exists
if [ -f "$CONFIG_FILE" ]; then
    ln -sf "$CONFIG_FILE" /var/www/fusionpbx/resources/config.php 2>/dev/null || true
fi

# Test nginx configuration
echo "Testing Nginx configuration..."
nginx -t

echo "=== Starting services ==="

# Execute the main command
exec "$@"

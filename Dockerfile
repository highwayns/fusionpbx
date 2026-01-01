FROM debian:bullseye-slim

LABEL maintainer="FusionPBX Docker Build"
LABEL description="FusionPBX Web GUI for FreeSWITCH"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg2 \
    lsb-release \
    ca-certificates \
    git \
    nginx \
    ssl-cert \
    supervisor \
    # PHP 7.4 packages
    php7.4-fpm \
    php7.4-pgsql \
    php7.4-sqlite3 \
    php7.4-odbc \
    php7.4-curl \
    php7.4-imap \
    php7.4-xml \
    php7.4-gd \
    php7.4-mbstring \
    php7.4-cli \
    php7.4-json \
    # PostgreSQL client
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/www/fusionpbx \
    && mkdir -p /var/run/php \
    && mkdir -p /var/log/fusionpbx \
    && mkdir -p /etc/fusionpbx

# Clone FusionPBX
RUN git clone --depth 1 https://github.com/fusionpbx/fusionpbx.git /var/www/fusionpbx

# Set permissions
RUN chown -R www-data:www-data /var/www/fusionpbx \
    && chmod -R 755 /var/www/fusionpbx

# Configure PHP
RUN sed -i 's/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/' /etc/php/7.4/fpm/php.ini \
    && sed -i 's/upload_max_filesize = 2M/upload_max_filesize = 80M/' /etc/php/7.4/fpm/php.ini \
    && sed -i 's/post_max_size = 8M/post_max_size = 80M/' /etc/php/7.4/fpm/php.ini \
    && sed -i 's/memory_limit = 128M/memory_limit = 256M/' /etc/php/7.4/fpm/php.ini \
    && sed -i 's/;date.timezone =/date.timezone = Asia\/Tokyo/' /etc/php/7.4/fpm/php.ini

# Configure PHP-FPM pool
RUN sed -i 's/listen = \/run\/php\/php7.4-fpm.sock/listen = \/var\/run\/php\/php7.4-fpm.sock/' /etc/php/7.4/fpm/pool.d/www.conf

# Copy configuration files
COPY nginx-fusionpbx.conf /etc/nginx/sites-available/fusionpbx
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /entrypoint.sh

# Enable site
RUN rm -f /etc/nginx/sites-enabled/default \
    && ln -sf /etc/nginx/sites-available/fusionpbx /etc/nginx/sites-enabled/fusionpbx

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

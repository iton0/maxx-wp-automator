FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install SSH, Apache, PHP, and MySQL Client
RUN apt-get update && apt-get install -y \
    openssh-server apache2 php php-cli libapache2-mod-php \
    php-mysql php-curl php-gd php-mbstring php-xml \
    curl mariadb-client sudo unzip \
    && mkdir /var/run/sshd

# Install WP-CLI correctly
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && \
    chmod +x wp-cli.phar && \
    mv wp-cli.phar /usr/local/bin/wp

# Set up testuser
RUN useradd -ms /bin/bash testuser && \
    echo 'testuser:password' | chpasswd && \
    adduser testuser sudo

# Ensure the log and run directories for Apache are writable if needed
RUN mkdir -p /var/lock/apache2 /var/run/apache2

# IMPORTANT: Fix permissions for /var/www/html
# This ensures testuser (who SSHs in) can write files that Apache (www-data) can read
RUN chown -R testuser:www-data /var/www/html && \
    chmod -R 775 /var/www/html && \
    # Set the GID bit so new files created by testuser inherit the www-data group
    find /var/www/html -type d -exec chmod g+s {} +

# Configure SSH to allow password login (since your script uses --passw)
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Set the working directory
WORKDIR /var/www/html

EXPOSE 22 80

# Start services
CMD service apache2 start && /usr/sbin/sshd -D

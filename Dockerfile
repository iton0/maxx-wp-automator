FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install SSH, Apache, PHP, and MySQL Client
RUN apt-get update && apt-get install -y \
    openssh-server apache2 php libapache2-mod-php \
    php-mysql php-curl php-gd php-mbstring php-xml \
    curl mariadb-client sudo \
    && mkdir /var/run/sshd

# Install WP-CLI
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && \
    chmod +x wp-cli.phar && \
    mv wp-cli.phar /usr/local/bin/wp

# Set up testuser with sudo privileges
RUN useradd -ms /bin/bash testuser && \
    echo 'testuser:password' | chpasswd && \
    adduser testuser sudo

# Ensure SSH starts in /var/www/html for testuser
RUN echo "cd /var/www/html" >> /home/testuser/.bashrc

# Fix permissions so testuser can manage WordPress without root
RUN chown -R testuser:www-data /var/www/html && \
    chmod -R 775 /var/www/html

# Configure SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Set the working directory for 'docker exec' and 'docker run'
WORKDIR /var/www/html

EXPOSE 22 80

CMD service apache2 start && /usr/sbin/sshd -D

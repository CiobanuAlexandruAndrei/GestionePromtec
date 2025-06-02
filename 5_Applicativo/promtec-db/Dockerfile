FROM mysql:8.0.42

# Copy initialization shell script and environment variables
COPY init.sh /docker-entrypoint-initdb.d/
COPY .env /docker-entrypoint-initdb.d/

# Set executable permission for initialization scripts
RUN chmod +x /docker-entrypoint-initdb.d/*

# MySQL configuration if needed
# COPY my.cnf /etc/mysql/conf.d/

# Default port
EXPOSE 3306

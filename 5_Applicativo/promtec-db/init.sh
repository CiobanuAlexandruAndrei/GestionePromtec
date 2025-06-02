#!/bin/bash

# Load environment variables from .env file
if [ -f /docker-entrypoint-initdb.d/.env ]; then
  # When running in Docker, the .env file is mounted to docker-entrypoint-initdb.d
  source /docker-entrypoint-initdb.d/.env
elif [ -f ./.env ]; then
  # For local development
  source ./.env
else
  echo "Error: .env file not found"
  exit 1
fi

# MySQL command with environment variables
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<EOF
-- Grant specific permissions to the application user (everything except dangerous operations)
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE, CREATE VIEW, SHOW VIEW, EVENT, TRIGGER ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';

-- Apply changes
FLUSH PRIVILEGES;
EOF

# Print completion message
echo "Database permissions configured successfully"

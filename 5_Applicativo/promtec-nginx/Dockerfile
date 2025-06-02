FROM nginx:stable-alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create directory for certificates
RUN mkdir -p /etc/nginx/certs

# Copy SSL certificates
COPY certs/nginx.crt /etc/nginx/certs/
COPY certs/nginx.key /etc/nginx/certs/

# Expose both HTTP and HTTPS ports
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]

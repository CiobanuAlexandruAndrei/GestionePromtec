FROM node:20-alpine as build-stage

WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage

# Copy the built app to Nginx's serve directory
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom NGINX configuration for Vue Router
COPY default.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# Multi-stage build for React Admin Panel

# Stage 1: Base stage
FROM node:20-alpine as base

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Stage 2: Development stage
FROM base as development

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Development server with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage 3: Build stage
FROM base as builder

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Stage 4: Production stage with nginx
FROM nginx:alpine as production

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]



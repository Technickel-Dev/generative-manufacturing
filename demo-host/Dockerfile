FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port (Cloud Run sets PORT env var, but good for documentation)
EXPOSE 8080

# Command to run (serve.ts handles PORT and MODE)
CMD ["npm", "run", "serve"]

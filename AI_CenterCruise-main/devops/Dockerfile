FROM node:18-alpine
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build widget (will use runtime env vars)
RUN npm run build:widget

# Expose port
EXPOSE 8080

# Start backend app
CMD ["npm", "start"]

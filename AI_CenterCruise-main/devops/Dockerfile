FROM node:22-alpine
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Set environment variable for build
ENV WIDGET_SERVER_URL="https://cruise-ai-widget-620626195243.europe-central2.run.app/api/chat"
ENV NODE_ENV=production

# Build widget (will use runtime env vars)
RUN npm run build:widget

# Expose port
EXPOSE 3000

# Start backend app with logging
CMD ["npm", "start"]

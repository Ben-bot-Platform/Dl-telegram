# Use Node.js official image
FROM node:20

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the source code
COPY . .

# Expose port (if needed)
EXPOSE 3000

# Run the bot
CMD ["npm", "start"]
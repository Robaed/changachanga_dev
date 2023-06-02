# Use the official Node.js image as the base image
FROM node:18-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY . .

# Install the dependencies
RUN yarn install --frozen-lockfile

# Build the application
RUN yarn build

# Set the default port to 80
ENV PORT=80

# Expose the port
EXPOSE $PORT

# Start the application
CMD ["yarn", "start"]

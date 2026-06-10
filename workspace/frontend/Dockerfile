# 1. Install dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

# 2. Build the application
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Ensure the next.config.mjs is present before build
RUN if [ ! -f next.config.mjs ]; then \
      echo "/** @type {import('next').NextConfig} */\nconst nextConfig = { output: 'standalone' };\nexport default nextConfig;" > next.config.mjs; \
    fi

RUN npm run build

# 3. Production image
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy the standalone output
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]

FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN HUSKY=0 npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
RUN apk update && apk upgrade --no-cache
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json ./
RUN npm ci --omit=dev

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup
USER appuser

CMD ["node", "build"]

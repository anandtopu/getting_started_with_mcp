FROM node:26-bookworm-slim
WORKDIR /course
COPY . .
RUN npm ci --ignore-scripts && npm cache clean --force
USER 65532:65532
ENV LUMEN_BIND=0.0.0.0
EXPOSE 8000
ENTRYPOINT ["node", "--import", "tsx", "scripts/typescript_gateway.ts"]

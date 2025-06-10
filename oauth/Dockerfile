FROM node:20
WORKDIR /app
COPY oauth-server.js ./
RUN chmod 644 /app/oauth-server.js
RUN npm install oauth-provider express oauth2-server cors
EXPOSE 3000
CMD ["node", "oauth-server.js"] 
# ⚠️ MAUVAISE PRATIQUE #1: Image non spécifique (latest)
FROM node:latest

# ⚠️ MAUVAISE PRATIQUE #2: Pas de user non-root
WORKDIR /app

# ⚠️ MAUVAISE PRATIQUE #3: Copie de tout sans .dockerignore
COPY . .

# ⚠️ MAUVAISE PRATIQUE #4: npm install au lieu de npm ci
RUN npm install

# ⚠️ MAUVAISE PRATIQUE #5: Pas de multi-stage build
RUN npm run build

# ⚠️ MAUVAISE PRATIQUE #6: Port exposé mais pas documenté
EXPOSE 3000

# ⚠️ MAUVAISE PRATIQUE #7: Variables d'environnement sensibles
ENV API_KEY=sk-1234567890abcdef
ENV DATABASE_URL=postgresql://admin:password123@db:5432/mydb
ENV AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
ENV AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# ⚠️ MAUVAISE PRATIQUE #8: Pas de healthcheck
CMD ["npm", "start"]

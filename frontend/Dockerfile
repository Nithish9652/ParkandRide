FROM node:18-alpine
WORKDIR /usr/src/app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
CMD ["yarn","dev","-H","0.0.0.0"]
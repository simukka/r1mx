FROM ruby:3.3-alpine

RUN apk add --no-cache build-base git

WORKDIR /site

COPY Gemfile ./
RUN bundle install

COPY . .

EXPOSE 4000

CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--livereload", "--livereload-port", "35729"]

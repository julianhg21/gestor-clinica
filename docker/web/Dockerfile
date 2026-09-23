FROM nginx:1.27-alpine
COPY src/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY src/web/index.html /usr/share/nginx/html/index.html
COPY src/web/styles.css /usr/share/nginx/html/styles.css
COPY src/web/app.js /usr/share/nginx/html/app.js
EXPOSE 80

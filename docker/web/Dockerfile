FROM nginx:1.27-alpine
ENV NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1
COPY src/web/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY src/web/index.html /usr/share/nginx/html/index.html
COPY src/web/styles.css /usr/share/nginx/html/styles.css
COPY src/web/app.js /usr/share/nginx/html/app.js
COPY src/web/edit-modal.js /usr/share/nginx/html/edit-modal.js
EXPOSE 80

# =============================================================================

# st2web customized for running behind an oauth2 reverse proxy
#
# The stock st2web image ships st2-http and st2-https nginx
# templates plus its own entrypoint that renders one of them into
# /etc/nginx/conf.d/ based on environment variables. 
#
# Relying on that is fragile - the entrypoint can re-render at every start 
# and overwrite our config. 
#
# This image bakes in our bespoke nginx conf instead and trying to overwrite specific 
# parts of the base image's rendering step. 

# =============================================================================

ARG ST2_VERSION=latest
FROM stackstorm/st2web:${ST2_VERSION}

USER root

# Remove the stock configs AND the templates they are rendered from.
# Removing the templates files stops the image entrypoint re-creating them.
# ---------------------------------------------------------------------------
RUN rm -f /etc/nginx/conf.d/st2.conf \
          /etc/nginx/conf.d/st2-http.conf \
          /etc/nginx/conf.d/st2-https.conf \
          /etc/nginx/conf.d/default.conf \
    && rm -f /etc/nginx/conf.d/*.template \
             /etc/nginx/templates/*.template \
             /etc/nginx/st2-http.template \
             /etc/nginx/st2-https.template \
    && true

COPY st2.conf         /etc/nginx/conf.d/st2.conf
COPY snippets/        /etc/nginx/snippets/

# html page that - once authenticated via OIDC loads a StackStorm 
# session token into local storage for other stackstorm containers to work.
COPY auth.html /opt/stackstorm/static/webui/auth.html

RUN (command -v curl >/dev/null 2>&1) || \
    (apt-get update && apt-get install -y --no-install-recommends curl \
     && rm -rf /var/lib/apt/lists/*)

# Test the nginx config to make sure it compiles before building the image. 
# If the docker container fails here - check our bespoke st2.conf
RUN nginx -t

EXPOSE 8080

ENTRYPOINT ["nginx", "-g", "daemon off;"]

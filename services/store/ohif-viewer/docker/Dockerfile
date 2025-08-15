FROM docker.io/node:18-bullseye AS build

LABEL IMAGE="ohif"
LABEL VERSION="v3.10.1"
LABEL BUILD_IGNORE="False"

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    python3 \
    python3-distutils \
    python3-pip \
    build-essential \
  && rm -rf /var/lib/apt/lists/*


RUN git clone https://github.com/OHIF/Viewers.git /src && cd /src && git checkout 9a4a40468fc61e8c4818ea57905239bdff47f634

RUN yarn config set workspaces-experimental true

WORKDIR /src

COPY files/kaapana.js /src/platform/app/public/config/kaapana.js

ENV HTML_TEMPLATE="index.html"
ENV PUBLIC_URL="/ohif/"
ENV APP_CONFIG="config/kaapana.js"

COPY files/customization.patch /src/
RUN git apply customization.patch

RUN yarn install
RUN yarn run build

FROM docker.io/nginx:1.27.3-alpine AS production-stage

COPY --from=build /src/platform/app/dist/ /usr/share/nginx/html/ohif/

COPY files/ /usr/share/nginx/html/
COPY files/kaapana.js /usr/share/nginx/html/ohif/app-config.js

COPY conf /etc/nginx
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]



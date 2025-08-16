FROM docker.io/zwh188222/densematrix:base-python-cpu-latest

LABEL IMAGE="kube-helm"
LABEL VERSION="0.1.4"
LABEL BUILD_IGNORE="False"

WORKDIR /app

# Set versions for cli tools
ENV KUBE_VERSION="v1.33.0"
ENV HELM_VERSION="v3.17.3"
ENV CONTAINERD_VERSION="1.7.27"

## Install kubectl and helm cli tools (auto-detect arch)
RUN set -eux; \
    ARCH_RAW="$(uname -m)"; \
    case "$ARCH_RAW" in \
      aarch64) ARCH=arm64 ;; \
      x86_64)  ARCH=amd64 ;; \
      *)       ARCH="$ARCH_RAW" ;; \
    esac; \
    curl -fsSL -o kubectl "https://dl.k8s.io/release/${KUBE_VERSION}/bin/linux/${ARCH}/kubectl"; \
    chmod +x kubectl && mv ./kubectl /usr/local/bin/kubectl; \
    curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-${ARCH}.tar.gz" \
      | tar -xzO linux-${ARCH}/helm > /usr/local/bin/helm; \
    chmod +x /usr/local/bin/helm; \
    mkdir -p /config && chmod g+rwx /config

RUN apt-get update || true

# Install containerd cli tool
RUN set -eux; \
    ARCH_RAW="$(uname -m)"; \
    case "$ARCH_RAW" in \
      aarch64) ARCH=arm64 ;; \
      x86_64)  ARCH=amd64 ;; \
      *)       ARCH="$ARCH_RAW" ;; \
    esac; \
    curl -fsSL -o containerd.tar.gz \
      "https://github.com/containerd/containerd/releases/download/v${CONTAINERD_VERSION}/containerd-${CONTAINERD_VERSION}-linux-${ARCH}.tar.gz"; \
    tar -xf containerd.tar.gz; \
    cp bin/ctr /usr/local/bin/ctr && chmod +x /usr/local/bin/ctr; \
    rm -rf containerd* bin/

# Install pip packages
COPY files/requirements.txt /app/
RUN pip3 install -c https://codebase.helmholtz.cloud/kaapana/constraints/-/raw/0.4.0/constraints.txt -r /app/requirements.txt

# Copy all files for containers
COPY files/backend/ /app
COPY files/update-collections-chart /root/collections/update-collections-chart
COPY files/pull-docker-chart /root/helpers/pull-docker-chart

# Install app package for scripts
RUN pip3 install .

# Package helper charts via `helm package`
RUN /usr/local/bin/helm package /root/collections/update-collections-chart -d /root/collections
RUN /usr/local/bin/helm package /root/helpers/pull-docker-chart -d /root/helpers

# Set paths and other env vars
ENV HELM_PATH="/usr/local/bin/helm"
ENV KUBECTL_PATH="kubectl"
ENV HELM_EXTENSIONS_CACHE="/kaapana/mounted/extensions"
ENV HELM_PLATFORMS_CACHE="/kaapana/mounted/platforms"
ENV LOG_LEVEL="info"
ENV RECENT_UPDATE_CACHE="true"
ENV CONTAINERD_SOCK="/kaapana/mounted/containerd.sock"

EXPOSE 5000

CMD ["/bin/sh", "/app/boot.sh"]

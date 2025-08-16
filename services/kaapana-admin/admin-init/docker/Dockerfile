FROM docker.io/alpine:3.20.3

LABEL IMAGE="cert-init"
LABEL VERSION="0.0.1"
LABEL BUILD_IGNORE="False"

ENV KUBE_VERSION="v1.31.2"
# RUN apk add --no-cache kubectl --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/x86_64
RUN apk add --no-cache openssl bash jq curl
# Install kubectl matching container architecture (amd64/arm64)
RUN ARCH_RAW="$(apk --print-arch)" \
    && case "$ARCH_RAW" in \
         aarch64) ARCH=arm64 ;; \
         x86_64)  ARCH=amd64 ;; \
         *)       ARCH="$ARCH_RAW" ;; \
       esac \
    && curl -fsSL -o kubectl "https://dl.k8s.io/release/${KUBE_VERSION}/bin/linux/${ARCH}/kubectl" \
    && chmod +x kubectl \
    && mv ./kubectl /usr/local/bin/kubectl

WORKDIR /cert
COPY handle-secret.sh .
CMD ["./handle-secret.sh"]

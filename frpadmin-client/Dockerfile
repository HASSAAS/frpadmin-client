FROM alpine:3.22 AS download
ARG BUILD_ARCH
ARG FRP_VERSION=0.71.0
RUN apk add --no-cache curl tar \
    && case "$BUILD_ARCH" in amd64) ARCH=amd64 ;; aarch64) ARCH=arm64 ;; *) exit 1 ;; esac \
    && curl -fL --retry 3 "https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_${ARCH}.tar.gz" -o /tmp/frp.tar.gz \
    && tar -xzf /tmp/frp.tar.gz -C /tmp \
    && cp "/tmp/frp_${FRP_VERSION}_linux_${ARCH}/frpc" /frpc \
    && cp "/tmp/frp_${FRP_VERSION}_linux_${ARCH}/LICENSE" /LICENSE.frp
FROM python:3.12-alpine
ARG BUILD_ARCH
ARG BUILD_VERSION=1.0.0
LABEL io.hass.type="addon" io.hass.version="${BUILD_VERSION}" io.hass.arch="${BUILD_ARCH}"
COPY --from=download /frpc /usr/local/bin/frpc
COPY --from=download /LICENSE.frp /usr/share/licenses/frp/LICENSE
COPY client.py /app/client.py
CMD ["python3", "/app/client.py"]

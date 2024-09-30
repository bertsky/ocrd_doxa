ARG DOCKER_BASE_IMAGE
FROM $DOCKER_BASE_IMAGE
ARG VCS_REF
ARG BUILD_DATE
LABEL \
    maintainer="https://ocr-d.de/kontakt" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/bertsky/ocrd_doxa" \
    org.label-schema.build-date=$BUILD_DATE

WORKDIR /build/ocrd_doxa
COPY setup.py .
COPY ocrd_doxa/ocrd-tool.json .
COPY ocrd_doxa ./ocrd_doxa
COPY requirements.txt .
COPY README.md .
COPY Makefile .
RUN make install
RUN rm -rf /build/ocrd_doxa

WORKDIR /data
VOLUME ["/data"]

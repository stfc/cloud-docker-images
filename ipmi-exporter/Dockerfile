FROM golang:1.25-alpine AS build-stage

WORKDIR /
ENV GOBIN=/

# ipmi exporter version also goes in version.txt
RUN go install github.com/prometheus-community/ipmi_exporter@v1.10.1

FROM alpine:latest AS build-release-stage

WORKDIR /
COPY --from=build-stage /ipmi_exporter /bin/ipmi_exporter

RUN addgroup -S ipmi -g 58256 && adduser -S ipmi-exp -G ipmi

EXPOSE      9290
USER        ipmi-exp
ENTRYPOINT  [ "/bin/ipmi_exporter" ]
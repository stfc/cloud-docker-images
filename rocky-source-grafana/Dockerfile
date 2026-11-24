FROM harbor.stfc.ac.uk/stfc-cloud/stackhpc/rocky-source-grafana:yoga-20240510T114335

ARG GRAFANA_VERSION="10.4.19^security_01-1"

USER root

RUN dnf update -y && dnf install -y --enablerepo grafana grafana-${GRAFANA_VERSION} && dnf clean all -y && rm -rf /var/cache/dnf

USER grafana

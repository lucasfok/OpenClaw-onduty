# syntax=docker/dockerfile:1.7

ARG OPENCLAW_BASE_IMAGE=ghcr.io/openclaw/openclaw:latest
FROM ${OPENCLAW_BASE_IMAGE}

ENV CODEX_HOME=/home/openclaw/.codex
ENV HOME=/home/openclaw

USER root
RUN addgroup --system openclaw \
    && adduser --system --ingroup openclaw --home /home/openclaw openclaw \
    && mkdir -p /workspace "$CODEX_HOME" "$CODEX_HOME/skills" /etc/onduty /opt/onduty \
    && chown -R openclaw:openclaw /home/openclaw /workspace /etc/onduty /opt/onduty

COPY --chown=openclaw:openclaw scripts/runbook_runner.py /opt/onduty/runbook_runner.py
COPY --chown=openclaw:openclaw scripts/daily_agent.sh /opt/onduty/daily_agent.sh
COPY --chown=openclaw:openclaw scripts/select_responsible.py /opt/onduty/select_responsible.py
COPY --chown=openclaw:openclaw scripts/bootstrap_skills.sh /opt/onduty/bootstrap_skills.sh
COPY --chown=openclaw:openclaw runbook/onduty-checks.json /etc/onduty/runbook.json
COPY --chown=openclaw:openclaw runbook/rotation-team.json /etc/onduty/rotation-team.json
COPY --chown=openclaw:openclaw skills /opt/onduty/skills

RUN sed -i 's/\r$//' /opt/onduty/*.sh /opt/onduty/*.py \
    && chmod +x /opt/onduty/runbook_runner.py /opt/onduty/daily_agent.sh /opt/onduty/select_responsible.py /opt/onduty/bootstrap_skills.sh

WORKDIR /workspace
USER openclaw

ENTRYPOINT ["/opt/onduty/bootstrap_skills.sh"]
CMD ["bash"]

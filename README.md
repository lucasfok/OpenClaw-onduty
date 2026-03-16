# OpenClaw OnDuty: agente diário de verificações

Este projeto sobe um ambiente OpenClaw seguro + um agente agendado para executar checks diários do runbook e definir automaticamente a pessoa responsável da semana.

## Objetivo

- Executar automaticamente verificações de on-duty todos os dias.
- Validar ambientes diferentes (ex.: `prod`, `staging`, `dev`) com checks HTTP/TCP/comando.
- Definir **1 responsável por semana** com rotação justa (sem repetição até todos participarem).
- Persistir histórico de relatórios e skills sem expor filesystem do host.

## Segurança aplicada

- **Sem bind mount do host**.
- **Usuário não-root** (`openclaw`).
- **Root filesystem read-only** + `tmpfs` para `/tmp` e `/run`.
- **`cap_drop: ALL`** e **`no-new-privileges`**.

## Serviços

- `openclaw`: shell interativo para operações manuais.
- `onduty-agent`: serviço que roda `daily_agent.sh` e dispara o runbook uma vez por dia.

## Arquivos importantes

- Runbook de checks: `runbook/onduty-checks.json` (copiado para `/etc/onduty/runbook.json`).
- Time da rotação: `runbook/rotation-team.json` (copiado para `/etc/onduty/rotation-team.json`).
- Runner de checks: `/opt/onduty/runbook_runner.py`.
- Seletor de responsável semanal: `/opt/onduty/select_responsible.py`.
- Scheduler diário: `/opt/onduty/daily_agent.sh`.
- Skill embutida: `skills/onduty-runbook-checker`.

## Regra de rotação semanal

- O responsável é definido por semana ISO (`YYYY-Www`).
- Dentro da mesma semana, a pessoa não muda.
- Na semana seguinte, o próximo da fila é escolhido.
- A fila só repete alguém depois que todos tiverem sido escolhidos.
- Estado da rotação persiste em `/workspace/rotation/state.json`.

## Como subir

```bash
docker compose up -d --build
```

## Como acompanhar execução do agente

```bash
docker compose logs -f onduty-agent
```

## Onde ficam os relatórios

No volume `openclaw_workspace`, em:

- `/workspace/reports/latest-report.json`
- `/workspace/reports/report-<timestamp>.json`

Cada relatório inclui `responsible_person` da semana.

## Skills (instalação e persistência)

- Skills ficam em `/home/openclaw/.codex/skills`.
- O bootstrap copia a skill local `onduty-runbook-checker` para esse diretório se ainda não existir.
- Como `CODEX_HOME` está em volume nomeado (`openclaw_codex_home`), skills instaladas continuam após restart.

## Ajustar horário diário

No `docker-compose.yml`, no serviço `onduty-agent`:

- `DAILY_CHECK_UTC_HOUR`
- `DAILY_CHECK_UTC_MINUTE`

## Atualizar o time da rotação

Edite `runbook/rotation-team.json` com os nomes (entre 7 e 11, ou qualquer quantidade >= 2).

## Derrubar

```bash
docker compose down
```

Para remover também os dados persistidos:

```bash
docker compose down -v
```

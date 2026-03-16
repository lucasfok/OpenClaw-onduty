#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone


def iso_week_key(dt: datetime) -> str:
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_team(team):
    dedup = []
    seen = set()
    for name in team:
        if not isinstance(name, str):
            continue
        clean = name.strip()
        if not clean or clean in seen:
            continue
        dedup.append(clean)
        seen.add(clean)
    return dedup


def main():
    team_path = os.environ.get("ROTATION_TEAM_PATH", "/etc/onduty/rotation-team.json")
    state_path = os.environ.get("ROTATION_STATE_PATH", "/workspace/rotation/state.json")

    team_data = load_json(team_path)
    team = normalize_team(team_data.get("people", []))
    if len(team) < 2:
        raise ValueError("rotation team must contain at least 2 people")

    if os.path.exists(state_path):
        state = load_json(state_path)
    else:
        state = {}

    now = datetime.now(timezone.utc)
    week_key = iso_week_key(now)

    last_week = state.get("last_week")
    last_person = state.get("last_person")
    queue = state.get("queue", [])
    if not isinstance(queue, list):
        queue = []

    queue = [p for p in queue if p in team]
    for p in team:
        if p not in queue:
            queue.append(p)

    if last_week == week_key and last_person in team:
        person = last_person
    else:
        if not queue:
            queue = team[:]
        person = queue[0]
        queue = queue[1:] + [person]
        state["last_week"] = week_key
        state["last_person"] = person

    state["queue"] = queue
    state["team"] = team
    state["updated_at"] = now.isoformat()

    save_json(state_path, state)
    print(json.dumps({"week": week_key, "person": person}, ensure_ascii=False))


if __name__ == "__main__":
    main()

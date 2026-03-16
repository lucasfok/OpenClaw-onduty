# Weekly rotation

## Team file
`rotation-team.json` format:

```json
{
  "people": ["ana", "bruno", "carla"]
}
```

Rules:
- use unique non-empty names,
- keep stable ordering to keep predictable rotation.

## Selection behavior
- week key: ISO week (`YYYY-Www`),
- if the week already has an assignee, keep it,
- on new week, select next person in queue,
- rotate queue and persist state,
- only repeat after everyone appears once.

# Check types

## HTTP check
Required fields:
- `type`: `http`
- `url`

Optional fields:
- `method` (default: `GET`)
- `expected_status` (default: `200`)
- `expected_substring`
- `verify_tls` (default: `true`)
- `timeout_seconds` (default: `10`)

## TCP check
Required fields:
- `type`: `tcp`
- `host`
- `port`

Optional fields:
- `timeout_seconds` (default: `10`)

## Command check
Required fields:
- `type`: `command`
- `command`

Optional fields:
- `expected_exit_code` (default: `0`)
- `expected_stdout_substring`
- `timeout_seconds` (default: `10`)

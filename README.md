# engine-bytedance

Engine wrapper for **BytePlus ModelArk** — ByteDance's Seedream image models.

**3 image endpoints, from BytePlus's own documentation (captured 2026-11-04):**
`seedream-5-0-260128`, `seedream-4-5-251128`, `seedream-4-0-250828`. Dated model
ids on purpose: an alias that moves under the user is a catalogue that lies.

Every endpoint is `experimental` until a real call proves it.

## Setup

```
export ARK_API_KEY=...
```

Base URL: `https://ark.ap-southeast.bytepluses.com/api/v3` (their international
entity, per their docs).

## Shape

Images are one synchronous call: `POST /images/generations`, answer inline.
The response carries `data[]` with a URL or base64.

## Not carried yet: video

ModelArk's video create takes `POST /contents/generations/tasks` with a
**`content[]` array** rather than a flat prompt, and returns `content.video_url`
when `status` is `succeeded`. The engine has the task machinery, but the
payload adapter for that array is not written. Seedance is therefore absent
rather than half-supported — the same rule as every other gap in this fleet.

## Tests

```
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

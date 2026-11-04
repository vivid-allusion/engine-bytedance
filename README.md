# engine-bytedance

Engine wrapper for **BytePlus ModelArk** — ByteDance's Seedream image models.

**6 endpoints, from BytePlus's own documentation (captured 2026-11-04):**
3 image and 3 video.
Images: `seedream-5-0-260128`, `seedream-4-5-251128`, `seedream-4-0-250828`.
Video: `dreamina-seedance-2-5-260628`, `dreamina-seedance-2-0-260128`,
`dreamina-seedance-1-5-pro`. Dated model
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

## Video: the content array

ModelArk's video create is `POST /contents/generations/tasks` with a **`content[]`
array** rather than a flat prompt — text and reference images are items in that
array, and `ratio` / `duration` / `watermark` ride beside it. The catalogue
carries `payload_style = "content_array"`, and the Engine builds the array from
the same profile a text-to-image run uses. One model id therefore serves both
text-to-video and image-to-video: the presence of a reference image is the
difference, which is exactly how BytePlus models it.

A completed task answers `status: succeeded` with `content.video_url`.

## Tests

```
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

# engine-bytedance

Engine wrapper for **BytePlus ModelArk** — ByteDance's Seedream image models.

**14 endpoints, from BytePlus's own documentation (captured 2026-11-04 and
2026-11-07):** 6 image and 8 video.

Images: `dola-seedream-5-0-pro-260628`, `dola-seedream-5-0-flash-260915`,
`seedream-5-0-260128`, `seedream-4-5-251128`, `seedream-4-0-250828`,
`seedream-3-0`.

Video: `dreamina-seedance-2-5-260628`, `dreamina-seedance-2-0-260128`,
`dreamina-seedance-2-0-fast-260128`, `dreamina-seedance-2-0-mini-260615`,
`seedance-1-5-pro`, `seedance-1-0-pro`, `seedance-1-0-pro-fast`,
`seedance-1-0-lite`. Dated model
ids on purpose: an alias that moves under the user is a catalogue that lies.

Every endpoint is `experimental` until a real call proves it.

## Resolutions and 4k

`resolution` is a select on the video entries, so the wizard offers only values
the catalogue knows about.

- **Seedance 2.0** takes `4k` (3840×2160 at 16:9, 10-bit, H.265/HEVC) on any
  activated account. BytePlus documents it.
- **Seedance 2.5** takes `4k` only on the whitelist-only Premium model
  (`dreamina-seedance-2-5-premium-260915`). The public reference stops at
  1080p, and an account outside that program gets the request rejected — the
  parameter note says so, so the option is never mistaken for a promise.
- **Drafts** preview at 480p; finishing a draft sends `4k` when the profile asks
  for it and `1080p` otherwise, which is the only value BytePlus accepts from a
  non-Premium account.

The quotes behind every claim are in
`engine-bytedance-docs/_sources/2026-11-11/seedance-resolutions.md`.

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

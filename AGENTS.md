# AGENTS.md — engine-bytedance

Notes for anyone changing this Engine: the Helmer Engine for BytePlus ModelArk
(Seedream images, Seedance video). The key is `ARK_API_KEY`. The Engine
contract lives in helmer-transceiver at `docs/architecture/ENGINE_CONTRACT.md`.

## Shape

- Images are one synchronous `POST /images/generations`; the answer is inline.
- Video is `POST /contents/generations/tasks` with a `content[]` array, then
  polled to a terminal state. The catalogue marks it with
  `payload_style = "content_array"`.

## Rules

1. **The catalogue is data.** One TOML per model under
   `engine_bytedance/endpoints/IMG-Models` and
   `engine_bytedance/endpoints/VID-Models`. Adding a model is a TOML file,
   never a branch in `engine_bytedance/engine.py`.
2. **`engine.py` holds no wire knowledge.** URLs, envelopes and terminal states
   live in `engine_bytedance/transport.py` and `engine_bytedance/tasks.py`.
3. **Never invent a model, a parameter or a price.** Each comes from
   BytePlus's own docs. Model ids are dated on purpose: an alias that moves
   under the user is a catalogue that lies.
4. **Fail loud.** A success with no file, an undeclared parameter sent, a job
   that never finishes — each is an error with a message, never a shrug.

## Tests

```
pip install -r requirements.txt -r requirements-dev.txt && python -m pytest -q
```

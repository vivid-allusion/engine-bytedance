"""The four answers the conformance suite needs from BytePlus.

Only images are catalogued today: video create on ModelArk takes a content[]
array rather than a flat prompt, and that adapter is not written yet.
"""

from __future__ import annotations

from engine_conformance import Behaviours, Call, Connector, Provider


class BytePlusConnector(Connector):
    package = "engine_bytedance"

    entries = {"text_to_image": "IMG-Models/seedream-5-0-260128.toml"}

    provider_modules = ()
    supports_polling = False

    def install(self, monkeypatch, behaviours: Behaviours) -> Provider:
        provider = Provider()
        state = {"submit": list(behaviours.submit_errors)}

        class FakeClient:
            def request_json(self, method, path, payload=None, *, headers=None, params=None):
                provider.calls.append(Call(kind="submit", payload=payload, path=path))
                if behaviours.submit_error is not None:
                    raise behaviours.submit_error
                if state["submit"]:
                    raise state["submit"].pop(0)
                return {"data": [{"url": url} for url in behaviours.result_urls]}

            def request_form(self, method, path, fields, *, files=None):
                return self.request_json(method, path, fields)

            def request_bytes(self, method, path):
                return behaviours.result_bytes

            def download(self, url):
                provider.downloads.append(url)
                provider.calls.append(Call(kind="download", url=url))
                if behaviours.download_error is not None:
                    raise behaviours.download_error
                return behaviours.result_bytes

        fake = FakeClient()
        monkeypatch.setattr(self.engine_class(), "_client", lambda _self: fake)
        return provider

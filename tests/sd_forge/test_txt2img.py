import httpx
import pytest

from src.services.sd_forge import SdForgeService


def _server_available(base_url: str) -> bool:
    try:
        with httpx.Client(timeout=2.0) as c:
            r = c.get(f"{base_url}/sdapi/v1/sd-models")
            r.raise_for_status()
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _server_available("http://127.0.0.1:7860"), reason="sd-forge server not available")
def test_txt2img_minimal():
    svc = SdForgeService()
    resp = svc.create_text2image(
        prompt="a cute cat, high quality",
        negative_prompt="",
        width=512,
        height=512,
        steps=10,
        cfg_scale=7.0,
        sampler_name="DPM++ 2M Karras",
        seed=42,
        n_iter=1,
        batch_size=1,
        loras=None,
        timeout=60.0,
    )
    assert isinstance(resp, dict)
    # Typical response contains base64 images list
    assert "images" in resp and isinstance(resp["images"], list)
    assert len(resp["images"]) >= 1

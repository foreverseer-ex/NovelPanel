"""
civitai 服务
"""

import hashlib
from pathlib import Path
from typing import Optional, Dict, Any

import httpx
import aiofiles

from schemas.model_meta import Example, GenerateArg, ModelMeta
from settings.app_setting import app_settings


class CivitaiService:
    """
    Civitai 服务
    """

    @staticmethod
    def test_connect() -> bool:
        """
        测试连接 Civitai API。

        :return: 是否连接成功
        """
        url = f"{app_settings.civitai.base_url}/api/v1/models"
        with httpx.Client(
                timeout=app_settings.civitai.timeout
        ) as client:
            resp = client.get(url)
            return resp.status_code == 200


    @staticmethod
    def _sha256(file_path: Path, buffer_size: int = 65536) -> str:
        """以流式方式计算文件的 SHA-256。

        :param file_path: 文件路径
        :param buffer_size: 读取块大小
        :return: 十六进制摘要字符串
        """
        h = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(buffer_size), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def get_model_detail_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
        """
        获取模型详情（包含图片 URL）。

        :param file_hash: 模型哈希值
        :return: 模型详情（包含图片 URL）
        """
        url = f"{app_settings.civitai.base_url}/api/v1/model-versions/by-hash/{file_hash}"
        with httpx.Client(
                timeout=app_settings.civitai.timeout
        ) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return None
            return resp.json()


    @classmethod
    def get_model_detail_by_path(cls, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        获取 safetensor 文件的模型详情。

        :param file_path: safetensor 文件路径
        :return: 模型详情（包含图片 URL）
        """
        if not file_path.exists() or file_path.suffix.lower() != ".safetensors":
            return None
        file_hash = cls._sha256(file_path)
        return cls.get_model_detail_by_hash(file_hash)

    @staticmethod
    async def download_image(url: str, save_path: Path) -> bool:
        """
        异步下载图片。

        :param url: 图片 URL
        :param save_path: 图片保存路径
        :return: 是否下载成功
        """
        async with httpx.AsyncClient(timeout=app_settings.civitai.timeout) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return False

            save_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(resp.content)
            return True

    @classmethod
    def get_model_meta_by_path(cls, file_path: Path) -> Optional[ModelMeta]:
        """
        获取 safetensor 文件的模型元数据。

        :param file_path: safetensor 文件路径
        :return: 模型元数据
        """
        detail = cls.get_model_detail_by_path(file_path)
        if not detail:
            return None
        examples: list[Example] = []
        for image_detail in detail["images"]:
            examples.append(
                Example(
                    url=image_detail["url"],
                    args=GenerateArg(
                        width=image_detail["metadata"]["width"],
                        height=image_detail["metadata"]["height"],
                        seed=image_detail["meta"]["seed"],
                        model=image_detail["meta"]["Model"],
                        steps=image_detail["meta"]["steps"],
                        prompt=image_detail["meta"]["prompt"],
                        sampler=image_detail["meta"]["sampler"],
                        cfg_scale=image_detail["meta"]["cfgScale"],
                        negative_prompt=image_detail["meta"]["negativePrompt"],
                    ),
                )
            )

        model_meta = ModelMeta(
            filename=file_path.name,
            name=detail["model"]["name"],
            version=detail["name"],
            desc=detail["description"],
            model_id=detail["modelId"],
            type=detail["model"]["type"],
            base_model=detail["baseModel"],
            sha256=detail["files"][0]["hashes"]["SHA256"],
            trained_words=detail["trainedWords"],
            download_url=detail["files"][0]["downloadUrl"],
            examples=examples,
        )
        return model_meta


civitai_service = CivitaiService()

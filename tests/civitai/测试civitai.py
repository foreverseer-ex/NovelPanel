import os
import time

import httpx

os.environ["CIVITAI_API_TOKEN"] = "044965df122445771b2f418d79297241"
import civitai
"""
Spec
urn:air:{ecosystem}:{type}:{source}:{id}@{version?}:{layer?}.?{format?}

urn: Uniform Resource Name
air: Artificial Intelligence Resource (or maybe AI Resource Name)arn
{ecosystem}: Type of the ecosystem (, , sd1sd2sdxl)
{type}: Type of the resource (, , , modelloraembeddinghypernet)
{source}: Supported network source
{id}: Id of the resource from the source
{layer}: The specific layer of a model
{format}: The format of the model (, , , safetensorckptdiffusertensor rt)
Examples
urn:air:sd1:model:civitai:2421@43533
urn:air:sd2:model:civitai:2421@43533
urn:air:sdxl:lora:civitai:328553@368189
urn:air:dalle:model:openai:dalle@2
urn:air:gpt:model:openai:gpt@4
urn:air:model:huggingface:stabilityai/sdxl-vae
urn:air:model:leonardo:345435

"""



option = {
    "model": "urn:air:sd1:checkpoint:civitai:4384@128713",
    "params": {
        "prompt": "masterpiece, best quality, 1girl, IncrsAhri, multiple tails, fox tail, korean clothes, skirt, braid, arms behind back",
        "negativePrompt": "(worst quality:1.4), (low quality:1.4), simple background, bad anatomy",
        "scheduler": "EulerA",
        "steps": 25,
        "cfgScale": 7,
        "width": 512,
        "height": 768,
        "seed": -1,
        "clipSkip": 2
    },
    "additionalNetworks": {
        "urn:air:sd1:lora:civitai:162141@182559": {
            "type": "Lora",
            "strength": 1.0
        }
    }
}
response = civitai.image.create(option)
token = response['token']
print('创建了任务')
print(token)
blob_url = None
while True:
    try:

        response = civitai.jobs.get(token=token)
    except httpx.ReadTimeout:
        time.sleep(1)
        continue

    available = response['jobs'][0]['result'][0]['available']
    if not available:
        continue
    else:
        blob_url = response['jobs'][0]['result'][0]['blob_url']
        break
print(blob_url)

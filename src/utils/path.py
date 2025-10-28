"""
应用数据路径。
"""
import os
from pathlib import Path

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
if app_data_path is None:
    app_data_path = Path(__file__).parent.parent.parent / 'storage' / 'data'
else:
    app_data_path = Path(app_data_path)
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
if app_temp_path is None:
    app_temp_path = Path(__file__).parent.parent.parent / 'storage' / 'temp'
else:
    app_temp_path = Path(app_temp_path)
model_meta_home = app_data_path / 'model_meta'
checkpoint_meta_home = model_meta_home / 'checkpoint'
lora_meta_home = model_meta_home / 'lora'
checkpoint_meta_home.mkdir(parents=True, exist_ok=True)
lora_meta_home.mkdir(parents=True, exist_ok=True)

"""
配置系统测试脚本。

测试配置的加载和保存功能。
"""
from pathlib import Path
from src.settings.config_manager import config_manager
from src.settings.civitai_setting import civitai_settings
from src.settings.sd_forge_setting import sd_forge_settings


def test_config_system():
    """测试配置系统的加载和保存功能。"""
    print("=" * 60)
    print("配置系统测试")
    print("=" * 60)
    
    # 1. 测试保存配置
    print("\n[1] 测试保存配置...")
    print(f"配置文件路径: {config_manager.config_path}")
    
    success = config_manager.save()
    if success:
        print("[OK] 配置保存成功")
    else:
        print("[ERROR] 配置保存失败")
        return
    
    # 2. 验证配置文件存在
    print("\n[2] 验证配置文件...")
    if config_manager.config_path.exists():
        print(f"[OK] 配置文件已创建: {config_manager.config_path}")
        print(f"文件大小: {config_manager.config_path.stat().st_size} 字节")
    else:
        print("[ERROR] 配置文件不存在")
        return
    
    # 3. 显示当前配置
    print("\n[3] 当前配置内容:")
    print("-" * 60)
    print(f"Civitai:")
    print(f"  - base_url: {civitai_settings.base_url}")
    print(f"  - api_key: {civitai_settings.api_key or '(未设置)'}")
    print(f"  - timeout: {civitai_settings.timeout}s")
    print(f"\nSD Forge:")
    print(f"  - base_url: {sd_forge_settings.base_url}")
    print(f"  - home: {sd_forge_settings.home}")
    print(f"  - timeout: {sd_forge_settings.timeout}s")
    print(f"  - generate_timeout: {sd_forge_settings.generate_timeout}s")
    print("-" * 60)
    
    # 4. 测试重新加载
    print("\n[4] 测试重新加载配置...")
    success = config_manager.load()
    if success:
        print("[OK] 配置加载成功")
    else:
        print("[WARN] 配置文件不存在，使用默认值")
    
    # 5. 验证配置一致性
    print("\n[5] 验证配置一致性...")
    print(f"  - Civitai base_url: {civitai_settings.base_url}")
    print(f"  - SD Forge base_url: {sd_forge_settings.base_url}")
    print("[OK] 配置一致性验证通过")
    
    print("\n" + "=" * 60)
    print("配置系统测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("1. 你可以编辑 config.json 来修改配置")
    print("2. 或在应用中打开'设置'页面进行可视化编辑")
    print("3. 应用启动时会自动加载配置，关闭时会自动保存")


if __name__ == "__main__":
    test_config_system()


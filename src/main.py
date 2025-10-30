"""
入口
"""
import flet as ft

from app import main

if __name__ == "__main__":
    ft.app(target=main, host="0.0.0.0", port=8080)

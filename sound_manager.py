#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音效管理模块 - SoundManager class

使用 ASCII 响铃字符 (chr(7)) 和转义序列生成简单音效。
"""

import sys
import time


class SoundManager:
    """音效管理类

    管理游戏音效的播放和开关状态。

    Attributes:
        enabled (bool): 音效是否开启
    """

    def __init__(self, enabled: bool = True):
        """初始化音效管理器

        Args:
            enabled: 音效是否默认开启
        """
        self.enabled = enabled

    def toggle(self):
        """切换音效开关状态"""
        self.enabled = not self.enabled
        return self.enabled

    def is_enabled(self) -> bool:
        """检查音效是否开启

        Returns:
            bool: 音效是否开启
        """
        return self.enabled

    def _beep(self, count: int = 1, delay: float = 0.05):
        """播放响铃音效

        Args:
            count: 响铃次数
            delay: 每次响铃之间的延迟（秒）
        """
        if not self.enabled:
            return
        for _ in range(count):
            sys.stdout.write(chr(7))
            sys.stdout.flush()
            if count > 1:
                time.sleep(delay)

    def play_shoot(self):
        """播放射击音效"""
        self._beep(1, 0.05)

    def play_enemy_death(self):
        """播放敌人死亡音效"""
        self._beep(2, 0.03)

    def play_player_hit(self):
        """播放玩家被击中音效"""
        self._beep(3, 0.08)

    def play_wave_clear(self):
        """播放波次清除音效"""
        self._beep(5, 0.1)

    def play_game_over(self):
        """播放游戏结束音效"""
        self._beep(4, 0.15)

    def __repr__(self) -> str:
        return f"SoundManager(enabled={self.enabled})"

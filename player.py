#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玩家模块 - Player class

管理玩家飞船的位置、移动、射击和生命值。
"""

from bullet import Bullet


class Player:
    """玩家类

    管理玩家飞船的状态、移动、射击和生命值。

    Attributes:
        x (int): 玩家飞船的列坐标
        y (int): 玩家飞船的行坐标（固定在最底部）
        lives (int): 剩余生命值
        bullets (list[Bullet]): 玩家发射的子弹列表
        invincible (bool): 是否处于无敌状态（重生后短暂无敌）
        invincible_timer (int): 无敌状态剩余帧数
    """

    CHAR = '^'
    START_LIVES = 3
    INVINCIBLE_FRAMES = 60  # 重生后无敌帧数

    def __init__(self, board_width: int, board_height: int):
        """初始化玩家

        Args:
            board_width: 游戏板宽度
            board_height: 游戏板高度
        """
        self.board_width = board_width
        self.board_height = board_height
        self.x = board_width // 2
        self.y = board_height - 1
        self.lives = self.START_LIVES
        self.bullets: list[Bullet] = []
        self.invincible = False
        self.invincible_timer = 0

    def reset_position(self):
        """重置玩家位置到屏幕中央"""
        self.x = self.board_width // 2
        self.y = self.board_height - 1
        self.invincible = True
        self.invincible_timer = self.INVINCIBLE_FRAMES

    def move_left(self):
        """向左移动一格"""
        if self.x > 0:
            self.x -= 1

    def move_right(self):
        """向右移动一格"""
        if self.x < self.board_width - 1:
            self.x += 1

    def shoot(self):
        """发射子弹

        从玩家当前位置向上发射一颗子弹。
        """
        bullet = Bullet(self.x, self.y - 1, -1, self.board_height)
        self.bullets.append(bullet)

    def update(self):
        """更新玩家状态

        更新子弹位置和无敌计时器。
        """
        # 更新无敌状态
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

    def hit(self) -> bool:
        """玩家被击中

        扣除一条生命。如果还有生命则重生。

        Returns:
            bool: 玩家是否还有剩余生命
        """
        if self.invincible:
            return True  # 无敌状态，不扣生命

        self.lives -= 1
        if self.lives > 0:
            self.reset_position()
            return True
        return False

    def __repr__(self) -> str:
        return f"Player(x={self.x}, y={self.y}, lives={self.lives})"

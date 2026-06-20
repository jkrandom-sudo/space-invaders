#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
子弹模块 - Bullet class

管理游戏中玩家和敌人的子弹。
"""


class Bullet:
    """子弹类

    管理子弹的位置、移动和活跃状态。
    方向: -1 向上（玩家子弹）, 1 向下（敌人子弹）

    Attributes:
        x (int): 子弹的列坐标
        y (int): 子弹的行坐标
        direction (int): 移动方向 (-1 向上, 1 向下)
        active (bool): 子弹是否活跃
    """

    CHAR = '|'
    DEFAULT_BOARD_HEIGHT = 20

    def __init__(self, x: int, y: int, direction: int, board_height: int = None):
        """初始化子弹

        Args:
            x: 起始列坐标
            y: 起始行坐标
            direction: 移动方向 (-1 向上, 1 向下)
            board_height: 游戏板高度（默认20）
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.active = True
        self.board_height = board_height if board_height is not None else self.DEFAULT_BOARD_HEIGHT

    def update(self):
        """更新子弹位置

        每帧调用一次，沿方向移动一格。
        超出游戏边界时标记为不活跃。
        """
        self.y += self.direction
        # 超出上下边界则失效
        if self.y < 0 or self.y > self.board_height + 10:
            self.active = False

    def __repr__(self) -> str:
        return f"Bullet(x={self.x}, y={self.y}, dir={self.direction}, active={self.active})"

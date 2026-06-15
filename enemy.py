#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敌人模块 - Enemy class

管理敌人的位置、移动、射击和编队行为。
"""

import random
from bullet import Bullet


class Enemy:
    """单个敌人

    Attributes:
        x (int): 敌人的列坐标
        y (int): 敌人的行坐标
        health (int): 敌人生命值
        active (bool): 敌人是否存活
    """

    CHAR = 'V'

    def __init__(self, x: int, y: int):
        """初始化敌人

        Args:
            x: 起始列坐标
            y: 起始行坐标
        """
        self.x = x
        self.y = y
        self.health = 1
        self.active = True

    def hit(self) -> bool:
        """敌人被击中

        Returns:
            bool: 敌人是否被消灭
        """
        self.health -= 1
        if self.health <= 0:
            self.active = False
            return True
        return False

    def __repr__(self) -> str:
        return f"Enemy(x={self.x}, y={self.y}, active={self.active})"


class EnemyGroup:
    """敌人类（编队）

    管理整组敌人的移动、射击和编队行为。

    Attributes:
        enemies (list[Enemy]): 敌人列表
        board_width (int): 游戏板宽度
        board_height (int): 游戏板高度
        direction (int): 水平移动方向 (1 右, -1 左)
        speed (int): 移动速度（每多少帧移动一次）
        move_counter (int): 移动计数器
        bullets (list[Bullet]): 敌人发射的子弹列表
        rows (int): 敌人行数
        cols (int): 敌人列数
        shoot_probability (float): 每帧每个敌人射击的概率
    """

    def __init__(self, board_width: int, board_height: int,
                 rows: int = 5, cols: int = 8, speed: int = 8):
        """初始化敌人编队

        Args:
            board_width: 游戏板宽度
            board_height: 游戏板高度
            rows: 敌人行数
            cols: 敌人列数
            speed: 移动速度（每多少帧移动一次，值越小越快）
        """
        self.board_width = board_width
        self.board_height = board_height
        self.direction = 1  # 1 向右, -1 向左
        self.speed = speed
        self.move_counter = 0
        self.bullets: list[Bullet] = []
        self.rows = rows
        self.cols = cols
        self.shoot_probability = 0.02
        self.enemies: list[Enemy] = []
        self._spawn_enemies()

    def _spawn_enemies(self):
        """生成敌人编队"""
        self.enemies = []
        # 计算左边距使编队居中
        left_margin = (self.board_width - self.cols * 3) // 2
        if left_margin < 1:
            left_margin = 1
        top_margin = 2

        for row in range(self.rows):
            for col in range(self.cols):
                x = left_margin + col * 3
                y = top_margin + row
                self.enemies.append(Enemy(x, y))

    def update(self):
        """更新敌人编队状态

        包括移动和射击。
        """
        # 移动逻辑（基于速度计数器）
        self.move_counter += 1
        if self.move_counter >= self.speed:
            self.move_counter = 0
            self._move()

        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

        # 随机射击
        self._shoot_random()

    def _move(self):
        """移动整个编队"""
        if not self.enemies:
            return

        # 检查是否到达边界
        hit_edge = False
        for enemy in self.enemies:
            if not enemy.active:
                continue
            if self.direction == 1 and enemy.x >= self.board_width - 1:
                hit_edge = True
                break
            if self.direction == -1 and enemy.x <= 0:
                hit_edge = True
                break

        if hit_edge:
            # 向下移动并反转方向
            self.direction *= -1
            for enemy in self.enemies:
                if enemy.active:
                    enemy.y += 1
        else:
            # 水平移动
            for enemy in self.enemies:
                if enemy.active:
                    enemy.x += self.direction

    def _shoot_random(self):
        """随机射击

        每个活跃敌人有一定概率发射子弹。
        """
        active_enemies = [e for e in self.enemies if e.active]
        if not active_enemies:
            return

        # 每个敌人有 shoot_probability 概率射击
        for enemy in active_enemies:
            if random.random() < self.shoot_probability:
                bullet = Bullet(enemy.x, enemy.y + 1, 1)
                self.bullets.append(bullet)

    def get_active_enemies(self) -> list[Enemy]:
        """获取所有活跃敌人

        Returns:
            list[Enemy]: 活跃敌人列表
        """
        return [e for e in self.enemies if e.active]

    def get_count(self) -> int:
        """获取活跃敌人数量

        Returns:
            int: 活跃敌人数量
        """
        return len(self.get_active_enemies())

    def has_reached_bottom(self) -> bool:
        """检查是否有敌人到达底部

        Returns:
            bool: 是否有敌人到达底部
        """
        for enemy in self.enemies:
            if enemy.active and enemy.y >= self.board_height - 1:
                return True
        return False

    def increase_difficulty(self):
        """增加难度

        增加行数并提高速度。
        """
        self.rows += 1
        if self.speed > 2:
            self.speed = max(2, int(self.speed * 0.9))
        self._spawn_enemies()

    def __repr__(self) -> str:
        return f"EnemyGroup(enemies={self.get_count()}, speed={self.speed})"

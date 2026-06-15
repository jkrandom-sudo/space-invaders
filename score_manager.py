#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分数管理模块 - ScoreManager class

管理游戏分数、最高分记录和持久化存储。
"""

import json
import os


class ScoreManager:
    """分数管理类

    管理当前分数、最高分记录，以及分数的持久化存储（JSON文件）。

    Attributes:
        score (int): 当前分数
        high_scores (list[dict]): 最高分记录列表
        scores_file (str): 分数存储文件路径
    """

    MAX_HIGH_SCORES = 5

    def __init__(self, scores_file: str = "scores.json"):
        """初始化分数管理器

        Args:
            scores_file: 分数存储文件路径
        """
        self.score = 0
        self.scores_file = scores_file
        self.high_scores: list[dict] = []
        self.load_scores()

    def add_score(self, points: int):
        """增加分数

        Args:
            points: 增加的分数
        """
        self.score += points

    def reset_score(self):
        """重置当前分数"""
        self.score = 0

    def get_score(self) -> int:
        """获取当前分数

        Returns:
            int: 当前分数
        """
        return self.score

    def load_scores(self):
        """从JSON文件加载最高分记录"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    self.high_scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.high_scores = []
        else:
            self.high_scores = []

    def save_scores(self):
        """保存最高分记录到JSON文件"""
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(self.high_scores, f, ensure_ascii=False, indent=2)
        except IOError:
            pass  # 如果无法写入，静默失败

    def is_high_score(self, score: int = None) -> bool:
        """检查分数是否可进入最高分榜

        Args:
            score: 要检查的分数，默认使用当前分数

        Returns:
            bool: 是否可进入最高分榜
        """
        if score is None:
            score = self.score
        if len(self.high_scores) < self.MAX_HIGH_SCORES:
            return True
        # 检查是否高于榜上最低分
        sorted_scores = sorted(self.high_scores,
                               key=lambda x: x.get('score', 0),
                               reverse=True)
        return score > sorted_scores[-1].get('score', 0)

    def add_high_score(self, name: str, score: int = None):
        """添加最高分记录

        Args:
            name: 玩家名称（3个字符）
            score: 分数，默认使用当前分数
        """
        if score is None:
            score = self.score
        self.high_scores.append({
            'name': name.upper()[:3],
            'score': score
        })
        # 排序并只保留前 N 条
        self.high_scores.sort(key=lambda x: x.get('score', 0), reverse=True)
        self.high_scores = self.high_scores[:self.MAX_HIGH_SCORES]
        self.save_scores()

    def get_high_scores(self) -> list[dict]:
        """获取最高分记录列表

        Returns:
            list[dict]: 最高分记录列表
        """
        return sorted(self.high_scores,
                      key=lambda x: x.get('score', 0),
                      reverse=True)

    def format_high_scores(self) -> str:
        """格式化最高分记录为显示字符串

        Returns:
            str: 格式化后的最高分显示文本
        """
        if not self.high_scores:
            return "暂无记录"

        lines = []
        scores = self.get_high_scores()
        for i, entry in enumerate(scores, 1):
            name = entry.get('name', '???')
            score = entry.get('score', 0)
            lines.append(f"  {i}. {name}  {score}")
        return '\n'.join(lines)

    def __repr__(self) -> str:
        return f"ScoreManager(score={self.score}, high_scores={len(self.high_scores)})"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏主模块 - Game class

太空侵略者（飞机大战）主游戏逻辑。
整合玩家、敌人、子弹、分数和音效管理。
"""

import sys
import time
import select

from bullet import Bullet
from enemy import Enemy, EnemyGroup
from player import Player
from score_manager import ScoreManager
from sound_manager import SoundManager


class Game:
    """游戏主类

    管理游戏循环、状态转换、渲染和输入处理。
    """

    BOARD_HEIGHT = 20
    BOARD_WIDTH = 30

    # 敌人波次配置
    ENEMY_ROWS = 5
    ENEMY_COLS = 8
    ENEMY_SPEED = 8

    # 帧率（秒）
    FRAME_DELAY = 0.1

    # 得分
    SCORE_PER_ENEMY = 100

    def __init__(self):
        """初始化游戏"""
        self.state = 'TITLE'  # TITLE, PLAYING, PAUSED, GAME_OVER
        self.level = 1

        # 创建游戏对象
        self.player = Player(self.BOARD_WIDTH, self.BOARD_HEIGHT)
        self.enemy_group = EnemyGroup(
            self.BOARD_WIDTH, self.BOARD_HEIGHT,
            rows=self.ENEMY_ROWS, cols=self.ENEMY_COLS,
            speed=self.ENEMY_SPEED
        )
        self.score_manager = ScoreManager()
        self.sound_manager = SoundManager()

        # 游戏运行标志
        self.running = True

        # 终端原始模式设置（用于非阻塞按键读取）
        self._old_term_settings = None
        try:
            self._fd = sys.stdin.fileno()
        except Exception:
            self._fd = None

    # ──────────────── 按键读取（跨平台，非阻塞） ────────────────

    def _setup_terminal(self):
        """设置终端为原始模式（Unix）"""
        if self._fd is None:
            return
        try:
            import termios
            import tty
            self._old_term_settings = termios.tcgetattr(self._fd)
            tty.setraw(self._fd)
        except ImportError:
            pass  # Windows 使用 msvcrt
        except Exception:
            pass

    def _restore_terminal(self):
        """恢复终端设置"""
        if self._fd is None or self._old_term_settings is None:
            return
        try:
            import termios
            termios.tcsetattr(self._fd, termios.TCSADRAIN,
                              self._old_term_settings)
        except ImportError:
            pass

    def _get_key(self) -> str:
        """非阻塞读取一个按键，无按键时返回空字符串"""
        try:
            # Windows
            import msvcrt  # type: ignore
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if isinstance(ch, bytes):
                    ch = ch.decode('utf-8', errors='ignore')
                # Validate single character
                if len(ch) == 1:
                    return ch
                return ''
            return ''
        except ImportError:
            # Unix — 使用 select 非阻塞检查
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                ch = sys.stdin.read(1)
                # Validate single character input
                if len(ch) == 1:
                    return ch
                return ''
            return ''

    # ──────────────── 游戏生命周期 ────────────────

    def reset_game(self):
        """重置游戏状态（重新开始）"""
        self.state = 'PLAYING'
        self.level = 1
        self.player = Player(self.BOARD_WIDTH, self.BOARD_HEIGHT)
        self.enemy_group = EnemyGroup(
            self.BOARD_WIDTH, self.BOARD_HEIGHT,
            rows=self.ENEMY_ROWS, cols=self.ENEMY_COLS,
            speed=self.ENEMY_SPEED
        )
        self.score_manager.reset_score()

    def run(self):
        """主游戏循环"""
        self._setup_terminal()
        try:
            while self.running:
                self._render()
                key = self._get_key()
                if key:
                    self._handle_input(key)
                self._update()
                time.sleep(self.FRAME_DELAY)
        finally:
            self._restore_terminal()

    # ──────────────── 渲染 ────────────────

    def _render(self):
        """渲染画面"""
        print('\033c', end='')

        if self.state == 'TITLE':
            self._render_title()
        elif self.state == 'PLAYING':
            self._render_game()
        elif self.state == 'PAUSED':
            self._render_game()
            self._render_pause_overlay()
        elif self.state == 'GAME_OVER':
            self._render_game_over()

    def _render_title(self):
        """渲染标题画面"""
        title_art = [
            "",
            "    ╔══════════════════════════╗",
            "    ║                          ║",
            "    ║     ✈  飞 机 大 战  ✈    ║",
            "    ║     Space Invaders       ║",
            "    ║                          ║",
            "    ╚══════════════════════════╝",
            "",
            "          🎮 操作说明",
            "          ──────────",
            "          A / D        移动左右",
            "          W / 空格     射击",
            "          P            暂停",
            "          S            音效开关",
            "          Q            退出",
            "",
            "      ⭐ 按任意键开始游戏 ⭐",
        ]
        for line in title_art:
            print(f"{line:^40}")

    def _render_game(self):
        """渲染游戏画面"""
        # 顶部信息栏
        score = self.score_manager.get_score()
        lives_display = '❤' * self.player.lives
        sound_status = '🔊' if self.sound_manager.is_enabled() else '🔇'
        print(f"  得分: {score:<6}  生命: {lives_display:<10}  关卡: {self.level}  {sound_status}")
        print("  " + "─" * self.BOARD_WIDTH)

        # 构建网格
        grid = [[' ' for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)]

        # 绘制敌人
        for enemy in self.enemy_group.enemies:
            if enemy.active:
                if 0 <= enemy.y < self.BOARD_HEIGHT and 0 <= enemy.x < self.BOARD_WIDTH:
                    grid[enemy.y][enemy.x] = Enemy.CHAR

        # 绘制敌人子弹
        for bullet in self.enemy_group.bullets:
            if bullet.active:
                if 0 <= bullet.y < self.BOARD_HEIGHT and 0 <= bullet.x < self.BOARD_WIDTH:
                    grid[bullet.y][bullet.x] = Bullet.CHAR

        # 绘制玩家
        if self.player.lives > 0:
            px, py = self.player.x, self.player.y
            if 0 <= py < self.BOARD_HEIGHT and 0 <= px < self.BOARD_WIDTH:
                # 无敌时闪烁显示
                if self.player.invincible and (int(time.time() * 5) % 2 == 0):
                    grid[py][px] = '*'
                else:
                    grid[py][px] = Player.CHAR

        # 绘制玩家子弹
        for bullet in self.player.bullets:
            if bullet.active:
                if 0 <= bullet.y < self.BOARD_HEIGHT and 0 <= bullet.x < self.BOARD_WIDTH:
                    grid[bullet.y][bullet.x] = Bullet.CHAR

        # 输出网格
        for row in grid:
            print("  " + "".join(row))

        print("  " + "─" * self.BOARD_WIDTH)

    def _render_pause_overlay(self):
        """渲染暂停覆盖层"""
        print()
        print(" " * 10 + "════════════════════")
        print(" " * 10 + "║      ⏸ 已暂停     ║")
        print(" " * 10 + "║   按 P 继续游戏   ║")
        print(" " * 10 + "════════════════════")

    def _render_game_over(self):
        """渲染游戏结束画面"""
        score = self.score_manager.get_score()
        print()
        print(" " * 8 + "╔══════════════════════╗")
        print(" " * 8 + "║                      ║")
        print(" " * 8 + "║     💥 游戏结束 💥    ║")
        print(" " * 8 + "║                      ║")
        print(" " * 8 + "╚══════════════════════╝")
        print()
        print(f"           最终得分: {score}")
        print()

        # 显示最高分榜
        high_scores = self.score_manager.get_high_scores()
        if high_scores:
            print("          🏆 最高分榜")
            print("          ─────────")
            print(f"          {self.score_manager.format_high_scores()}")
        print()
        print("       按 R 重新开始  |  按 Q 退出")

    # ──────────────── 输入处理 ────────────────

    def _handle_input(self, key: str):
        """处理按键输入"""
        key = key.lower()

        if self.state == 'TITLE':
            if key == 'q':
                self.running = False
            else:
                self.reset_game()
            return

        if self.state == 'GAME_OVER':
            if key == 'r':
                self.reset_game()
            elif key == 'q':
                self.running = False
            return

        if self.state == 'PLAYING':
            if key == 'q':
                self.running = False
            elif key == 'p':
                self.state = 'PAUSED'
            elif key == 's':
                self.sound_manager.toggle()
            elif key == 'a':
                self.player.move_left()
            elif key == 'd':
                self.player.move_right()
            elif key in ('w', ' '):
                self.player.shoot()
                self.sound_manager.play_shoot()
            return

        if self.state == 'PAUSED':
            if key == 'p':
                self.state = 'PLAYING'
            elif key == 'q':
                self.running = False
            # 其他按键在暂停状态时被忽略（保持暂停）

    # ──────────────── 游戏逻辑更新 ────────────────

    def _update(self):
        """更新游戏逻辑"""
        if self.state != 'PLAYING':
            return

        # 更新玩家（子弹移动 + 无敌计时器）
        self.player.update()

        # 更新敌人（移动 + 射击）
        self.enemy_group.update()

        # ── 碰撞检测：玩家子弹 vs 敌人 ──
        for p_bullet in self.player.bullets[:]:
            if not p_bullet.active:
                continue
            for enemy in self.enemy_group.enemies:
                if not enemy.active:
                    continue
                if p_bullet.x == enemy.x and p_bullet.y == enemy.y:
                    p_bullet.active = False
                    if enemy.hit():
                        self.score_manager.add_score(self.SCORE_PER_ENEMY)
                        self.sound_manager.play_enemy_death()
                    break

        # ── 碰撞检测：敌人子弹 vs 玩家 ──
        if self.player.lives > 0:
            for e_bullet in self.enemy_group.bullets[:]:
                if not e_bullet.active:
                    continue
                if (e_bullet.x == self.player.x and
                        e_bullet.y == self.player.y):
                    e_bullet.active = False
                    alive = self.player.hit()
                    self.sound_manager.play_player_hit()
                    if not alive:
                        self.state = 'GAME_OVER'
                        self.sound_manager.play_game_over()
                        if self.score_manager.is_high_score():
                            self.score_manager.add_high_score("PLR")
                    break

        # ── 检测敌人是否到达底部 ──
        if self.enemy_group.has_reached_bottom():
            self.state = 'GAME_OVER'
            self.sound_manager.play_game_over()
            if self.score_manager.is_high_score():
                self.score_manager.add_high_score("PLR")
            return

        # ── 检测是否清空当前波次 → 生成新波次 ──
        if self.enemy_group.get_count() == 0:
            self.sound_manager.play_wave_clear()
            self.level += 1
            # 每关增加难度：行数增加、速度加快
            new_rows = min(self.ENEMY_ROWS + self.level - 1, 8)
            new_speed = max(self.ENEMY_SPEED - (self.level - 1), 2)
            self.enemy_group = EnemyGroup(
                self.BOARD_WIDTH, self.BOARD_HEIGHT,
                rows=new_rows, cols=self.ENEMY_COLS,
                speed=new_speed
            )


if __name__ == '__main__':
    game = Game()
    game.run()

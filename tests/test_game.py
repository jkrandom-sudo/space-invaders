#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Space Invaders 游戏单元测试

测试覆盖：Bullet、Player、Enemy、EnemyGroup、ScoreManager、SoundManager、Game
使用 pytest + unittest.mock 避免交互式终端和终端输出。
"""

import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open, PropertyMock

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bullet
import player
import enemy
import score_manager
import sound_manager
import game


# ============================================================
# Bullet 测试
# ============================================================

class TestBullet:
    """子弹类测试"""

    def test_bullet_creation(self):
        """测试 Bullet 创建时属性正确"""
        b = bullet.Bullet(5, 10, -1)
        assert b.x == 5
        assert b.y == 10
        assert b.direction == -1
        assert b.active is True

    def test_bullet_update_moves_up(self):
        """测试子弹向上移动（direction=-1）"""
        b = bullet.Bullet(5, 10, -1)
        b.update()
        assert b.y == 9

    def test_bullet_update_moves_down(self):
        """测试子弹向下移动（direction=1）"""
        b = bullet.Bullet(5, 10, 1)
        b.update()
        assert b.y == 11

    def test_bullet_deactivates_when_out_of_bounds_top(self):
        """测试子弹超出上边界后 active 为 False"""
        b = bullet.Bullet(5, 0, -1)
        b.update()
        assert b.active is False

    def test_bullet_stays_active_within_bounds(self):
        """测试子弹在边界内保持活跃"""
        b = bullet.Bullet(5, 1, -1)
        b.update()
        assert b.active is True


# ============================================================
# Player 测试
# ============================================================

class TestPlayer:
    """玩家类测试"""

    BOARD_W = 30
    BOARD_H = 20

    def test_player_creation(self):
        """测试 Player 创建时属性正确"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        assert p.x == self.BOARD_W // 2
        assert p.y == self.BOARD_H - 1
        assert p.lives == 3
        assert p.invincible is False
        assert p.invincible_timer == 0
        assert p.bullets == []

    def test_player_move_left(self):
        """测试玩家左移一格"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.x = 10
        p.move_left()
        assert p.x == 9

    def test_player_move_right(self):
        """测试玩家右移一格"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.x = 10
        p.move_right()
        assert p.x == 11

    def test_player_move_left_boundary(self):
        """测试玩家左移不出左边界"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.x = 0
        p.move_left()
        assert p.x == 0

    def test_player_move_right_boundary(self):
        """测试玩家右移不出右边界"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.x = self.BOARD_W - 1
        p.move_right()
        assert p.x == self.BOARD_W - 1

    def test_player_shoot_creates_bullet(self):
        """测试玩家射击创建一颗向上子弹"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.shoot()
        assert len(p.bullets) == 1
        b = p.bullets[0]
        assert b.x == p.x
        assert b.y == p.y - 1
        assert b.direction == -1

    def test_player_update_removes_inactive_bullets(self):
        """测试 Player.update 移除已失效的子弹"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.shoot()
        # 让子弹飞出边界
        for _ in range(self.BOARD_H + 5):
            p.update()
        assert len(p.bullets) == 0

    def test_player_hit_reduces_lives(self):
        """测试玩家被击中减少一条生命"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.lives = 3
        p.invincible = False
        p.hit()
        assert p.lives == 2

    def test_player_hit_sets_invincible(self):
        """测试玩家被击中后进入无敌状态并重置位置"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.invincible = False
        p.hit()
        assert p.invincible is True
        assert p.invincible_timer == player.Player.INVINCIBLE_FRAMES

    def test_player_invincible_prevents_damage(self):
        """测试无敌状态下 hit() 不扣生命"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.lives = 3
        p.invincible = True
        result = p.hit()
        assert result is True
        assert p.lives == 3

    def test_player_hit_returns_false_when_dead(self):
        """测试生命为 0 时 hit() 返回 False"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.lives = 1
        p.invincible = False
        result = p.hit()
        assert result is False
        assert p.lives == 0

    def test_player_invincible_timer_expires(self):
        """测试无敌计时器归零后 invincible 变为 False"""
        p = player.Player(self.BOARD_W, self.BOARD_H)
        p.invincible = True
        p.invincible_timer = 3
        for _ in range(3):
            p.update()
        assert p.invincible is False
        assert p.invincible_timer == 0


# ============================================================
# Enemy 测试
# ============================================================

class TestEnemy:
    """敌人类测试"""

    def test_enemy_creation(self):
        """测试 Enemy 创建时属性正确"""
        e = enemy.Enemy(3, 4)
        assert e.x == 3
        assert e.y == 4
        assert e.health == 1
        assert e.active is True

    def test_enemy_hit_deactivates(self):
        """测试敌人被击中后 active 为 False"""
        e = enemy.Enemy(3, 4)
        result = e.hit()
        assert result is True
        assert e.active is False

    def test_enemy_hit_multi_health(self):
        """测试多生命值敌人需多次击中才消灭"""
        e = enemy.Enemy(3, 4)
        e.health = 3
        result1 = e.hit()
        assert result1 is False
        assert e.active is True
        e.hit()
        result3 = e.hit()
        assert result3 is True
        assert e.active is False


# ============================================================
# EnemyGroup 测试
# ============================================================

class TestEnemyGroup:
    """敌群类测试"""

    BOARD_W = 30
    BOARD_H = 20

    def test_group_creation(self):
        """测试 EnemyGroup 创建时生成正确数量的敌人"""
        eg = enemy.EnemyGroup(self.BOARD_W, self.BOARD_H, rows=3, cols=5)
        assert len(eg.enemies) == 15
        assert eg.direction == 1
        assert eg.speed == 8

    def test_group_get_count(self):
        """测试 get_count 返回活跃敌人数量"""
        eg = enemy.EnemyGroup(self.BOARD_W, self.BOARD_H, rows=2, cols=3)
        assert eg.get_count() == 6
        eg.enemies[0].active = False
        assert eg.get_count() == 5

    def test_group_get_count_zero_when_all_dead(self):
        """测试全部敌人消灭后 get_count 返回 0"""
        eg = enemy.EnemyGroup(self.BOARD_W, self.BOARD_H, rows=2, cols=3)
        for e in eg.enemies:
            e.active = False
        assert eg.get_count() == 0

    def test_group_has_reached_bottom_true(self):
        """测试敌人到达底部时 has_reached_bottom 返回 True"""
        eg = enemy.EnemyGroup(self.BOARD_W, self.BOARD_H)
        for e in eg.enemies:
            e.y = self.BOARD_H - 1
        assert eg.has_reached_bottom() is True

    def test_group_has_reached_bottom_false(self):
        """测试敌人未到达底部时 has_reached_bottom 返回 False"""
        eg = enemy.EnemyGroup(self.BOARD_W, self.BOARD_H)
        for e in eg.enemies:
            e.y = 5
        assert eg.has_reached_bottom() is False

    def test_group_move_changes_position(self):
        """测试 EnemyGroup.update 触发移动后敌人位置变化"""
        eg = enemy.EnemyGroup(self.BOARD_W, self.BOARD_H, speed=1)
        initial_x = eg.enemies[0].x
        # speed=1 意味着每帧都移动
        eg.update()
        # 初始 direction=1，应向右移动
        assert eg.enemies[0].x == initial_x + 1

    def test_group_move_reverses_at_edge(self):
        """测试敌人到达右边界时反转方向并下移"""
        eg = enemy.EnemyGroup(self.BOARD_W, self.BOARD_H, speed=1)
        # 把所有敌人放到右边界
        for e in eg.enemies:
            e.x = self.BOARD_W - 1
        initial_y = eg.enemies[0].y
        eg.update()
        # 方向应反转（变为 -1），且下移一行
        assert eg.direction == -1
        assert eg.enemies[0].y == initial_y + 1

    def test_group_increase_difficulty(self):
        """测试 increase_difficulty 增加行数并加速"""
        eg = enemy.EnemyGroup(self.BOARD_W, self.BOARD_H, rows=3, cols=5, speed=10)
        old_speed = eg.speed
        old_rows = eg.rows
        eg.increase_difficulty()
        assert eg.rows == old_rows + 1
        assert eg.speed < old_speed  # 速度值变小 = 更快
        assert len(eg.enemies) == eg.rows * eg.cols


# ============================================================
# ScoreManager 测试
# ============================================================

class TestScoreManager:
    """分数管理器测试"""

    @patch('score_manager.os.path.exists', return_value=False)
    def test_initial_score_zero(self, mock_exists):
        """测试初始分数为 0，高分列表为空"""
        sm = score_manager.ScoreManager("test_scores.json")
        assert sm.score == 0
        assert sm.high_scores == []

    @patch('score_manager.os.path.exists', return_value=False)
    def test_add_score(self, mock_exists):
        """测试 add_score 累加分数"""
        sm = score_manager.ScoreManager("test_scores.json")
        sm.add_score(100)
        assert sm.score == 100
        sm.add_score(50)
        assert sm.score == 150

    @patch('score_manager.os.path.exists', return_value=False)
    def test_reset_score(self, mock_exists):
        """测试 reset_score 将分数归零"""
        sm = score_manager.ScoreManager("test_scores.json")
        sm.add_score(200)
        sm.reset_score()
        assert sm.score == 0

    @patch('score_manager.os.path.exists', return_value=False)
    def test_get_score(self, mock_exists):
        """测试 get_score 返回当前分数"""
        sm = score_manager.ScoreManager("test_scores.json")
        sm.add_score(300)
        assert sm.get_score() == 300

    @patch('score_manager.os.path.exists', return_value=False)
    def test_is_high_score_when_list_not_full(self, mock_exists):
        """测试高分列表未满时任意分数都是高分"""
        sm = score_manager.ScoreManager("test_scores.json")
        assert sm.is_high_score(1) is True

    @patch('score_manager.os.path.exists', return_value=False)
    def test_is_high_score_when_list_full(self, mock_exists):
        """测试高分列表已满时需高于最低分才算高分"""
        sm = score_manager.ScoreManager("test_scores.json")
        sm.high_scores = [
            {'name': 'AAA', 'score': 500},
            {'name': 'BBB', 'score': 400},
            {'name': 'CCC', 'score': 300},
            {'name': 'DDD', 'score': 200},
            {'name': 'EEE', 'score': 100},
        ]
        assert sm.is_high_score(150) is True
        assert sm.is_high_score(100) is False
        assert sm.is_high_score(50) is False

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('score_manager.ScoreManager.save_scores')
    def test_add_high_score(self, mock_save, mock_exists):
        """测试 add_high_score 添加并排序高分"""
        sm = score_manager.ScoreManager("test_scores.json")
        sm.add_high_score("ABC", 300)
        sm.add_high_score("XYZ", 500)
        assert len(sm.high_scores) == 2
        assert sm.high_scores[0]['score'] == 500
        assert sm.high_scores[1]['score'] == 300

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('score_manager.ScoreManager.save_scores')
    def test_add_high_score_max_limit(self, mock_save, mock_exists):
        """测试高分列表不超过 MAX_HIGH_SCORES（5条）"""
        sm = score_manager.ScoreManager("test_scores.json")
        for i in range(10):
            sm.add_high_score(f"P{i:02d}", i * 100)
        assert len(sm.high_scores) <= sm.MAX_HIGH_SCORES

    @patch('score_manager.os.path.exists', return_value=False)
    def test_format_high_scores_empty(self, mock_exists):
        """测试无高分记录时 format_high_scores 返回提示"""
        sm = score_manager.ScoreManager("test_scores.json")
        assert sm.format_high_scores() == "暂无记录"

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('score_manager.ScoreManager.save_scores')
    def test_add_high_score_name_upper_truncated(self, mock_save, mock_exists):
        """测试 add_high_score 将名称转为大写并截断为3字符"""
        sm = score_manager.ScoreManager("test_scores.json")
        sm.add_high_score("player", 100)
        assert sm.high_scores[0]['name'] == "PLA"

    @patch('score_manager.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open,
           read_data=json.dumps([{'name': 'OLD', 'score': 999}]))
    def test_load_scores(self, mock_file, mock_exists):
        """测试 load_scores 从文件加载高分记录"""
        sm = score_manager.ScoreManager("test_scores.json")
        assert len(sm.high_scores) == 1
        assert sm.high_scores[0]['score'] == 999

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    def test_save_scores(self, mock_file, mock_exists):
        """测试 save_scores 将高分写入文件"""
        sm = score_manager.ScoreManager("test_scores.json")
        sm.high_scores = [{'name': 'TST', 'score': 777}]
        sm.save_scores()
        mock_file.assert_called_once_with("test_scores.json", 'w', encoding='utf-8')


# ============================================================
# SoundManager 测试
# ============================================================

class TestSoundManager:
    """音效管理器测试"""

    def test_initial_enabled(self):
        """测试 SoundManager 默认开启音效"""
        sm = sound_manager.SoundManager()
        assert sm.enabled is True
        assert sm.is_enabled() is True

    def test_initial_disabled(self):
        """测试 SoundManager 可传入 enabled=False 关闭音效"""
        sm = sound_manager.SoundManager(enabled=False)
        assert sm.enabled is False

    def test_toggle(self):
        """测试 toggle 切换音效开关"""
        sm = sound_manager.SoundManager()
        sm.toggle()
        assert sm.enabled is False
        sm.toggle()
        assert sm.enabled is True

    @patch('sound_manager.SoundManager._beep')
    def test_play_shoot(self, mock_beep):
        """测试 play_shoot 调用 _beep(1, 0.05)"""
        sm = sound_manager.SoundManager()
        sm.play_shoot()
        mock_beep.assert_called_once_with(1, 0.05)

    @patch('sound_manager.SoundManager._beep')
    def test_play_enemy_death(self, mock_beep):
        """测试 play_enemy_death 调用 _beep(2, 0.03)"""
        sm = sound_manager.SoundManager()
        sm.play_enemy_death()
        mock_beep.assert_called_once_with(2, 0.03)

    @patch('sound_manager.SoundManager._beep')
    def test_play_player_hit(self, mock_beep):
        """测试 play_player_hit 调用 _beep(3, 0.08)"""
        sm = sound_manager.SoundManager()
        sm.play_player_hit()
        mock_beep.assert_called_once_with(3, 0.08)

    @patch('sound_manager.SoundManager._beep')
    def test_play_wave_clear(self, mock_beep):
        """测试 play_wave_clear 调用 _beep(5, 0.1)"""
        sm = sound_manager.SoundManager()
        sm.play_wave_clear()
        mock_beep.assert_called_once_with(5, 0.1)

    @patch('sound_manager.SoundManager._beep')
    def test_play_game_over(self, mock_beep):
        """测试 play_game_over 调用 _beep(4, 0.15)"""
        sm = sound_manager.SoundManager()
        sm.play_game_over()
        mock_beep.assert_called_once_with(4, 0.15)

    @patch('sys.stdout')
    def test_beep_does_nothing_when_disabled(self, mock_stdout):
        """测试音效关闭时 _beep 不输出"""
        sm = sound_manager.SoundManager(enabled=False)
        sm._beep(3, 0.05)
        mock_stdout.write.assert_not_called()


# ============================================================
# Game 测试
# ============================================================

class TestGame:
    """游戏主类测试"""

    @patch('sys.stdin')
    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_initial_state_title(self, mock_select, mock_exists, mock_stdin):
        """测试 Game 初始状态为 TITLE"""
        g = game.Game()
        assert g.state == 'TITLE'
        assert g.level == 1
        assert g.running is True

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_reset_game_sets_playing(self, mock_select, mock_exists):
        """测试 reset_game 将状态设为 PLAYING"""
        g = game.Game()
        g.reset_game()
        assert g.state == 'PLAYING'

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_reset_game_resets_level(self, mock_select, mock_exists):
        """测试 reset_game 重置关卡为 1"""
        g = game.Game()
        g.level = 5
        g.reset_game()
        assert g.level == 1

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_reset_game_resets_score(self, mock_select, mock_exists):
        """测试 reset_game 重置分数为 0"""
        g = game.Game()
        g.score_manager.add_score(500)
        g.reset_game()
        assert g.score_manager.score == 0

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_reset_game_resets_player_lives(self, mock_select, mock_exists):
        """测试 reset_game 重置玩家生命为 3"""
        g = game.Game()
        g.player.lives = 1
        g.reset_game()
        assert g.player.lives == 3

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_title_to_playing(self, mock_select, mock_exists):
        """测试 TITLE 状态下按任意键进入 PLAYING"""
        g = game.Game()
        assert g.state == 'TITLE'
        g._handle_input(' ')
        assert g.state == 'PLAYING'

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_title_quit(self, mock_select, mock_exists):
        """测试 TITLE 状态下按 q 退出"""
        g = game.Game()
        g._handle_input('q')
        assert g.running is False

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_playing_to_paused(self, mock_select, mock_exists):
        """测试 PLAYING 状态下按 p 暂停"""
        g = game.Game()
        g.reset_game()
        assert g.state == 'PLAYING'
        g._handle_input('p')
        assert g.state == 'PAUSED'

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_paused_to_playing(self, mock_select, mock_exists):
        """测试 PAUSED 状态下按 p 继续游戏"""
        g = game.Game()
        g.reset_game()
        g.state = 'PAUSED'
        g._handle_input('p')
        assert g.state == 'PLAYING'

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_game_over_to_restart(self, mock_select, mock_exists):
        """测试 GAME_OVER 状态下按 r 重新开始"""
        g = game.Game()
        g.state = 'GAME_OVER'
        g._handle_input('r')
        assert g.state == 'PLAYING'

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_game_over_quit(self, mock_select, mock_exists):
        """测试 GAME_OVER 状态下按 q 退出"""
        g = game.Game()
        g.state = 'GAME_OVER'
        g._handle_input('q')
        assert g.running is False

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_playing_move_left(self, mock_select, mock_exists):
        """测试 PLAYING 状态下按 a 左移"""
        g = game.Game()
        g.reset_game()
        old_x = g.player.x
        g._handle_input('a')
        assert g.player.x == old_x - 1

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_playing_move_right(self, mock_select, mock_exists):
        """测试 PLAYING 状态下按 d 右移"""
        g = game.Game()
        g.reset_game()
        old_x = g.player.x
        g._handle_input('d')
        assert g.player.x == old_x + 1

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_playing_shoot(self, mock_select, mock_exists):
        """测试 PLAYING 状态下按空格射击"""
        g = game.Game()
        g.reset_game()
        g._handle_input(' ')
        assert len(g.player.bullets) == 1

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_handle_input_playing_toggle_sound(self, mock_select, mock_exists):
        """测试 PLAYING 状态下按 s 切换音效"""
        g = game.Game()
        g.reset_game()
        old_enabled = g.sound_manager.enabled
        g._handle_input('s')
        assert g.sound_manager.enabled is not old_enabled


# ============================================================
# 碰撞检测测试
# ============================================================

class TestCollision:
    """碰撞检测逻辑测试"""

    BOARD_W = 30
    BOARD_H = 20

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_player_bullet_hits_enemy(self, mock_select, mock_exists):
        """测试玩家子弹击中敌人：子弹失效、敌人消灭、加分"""
        g = game.Game()
        g.reset_game()
        # 子弹方向-1（向上），update会先移动子弹到y=10
        b = bullet.Bullet(10, 11, -1)
        g.player.bullets.append(b)
        # 在相同位置放一个敌人（子弹更新后到达的位置）
        e = enemy.Enemy(10, 10)
        g.enemy_group.enemies = [e]
        g._update()
        assert b.active is False
        assert e.active is False
        assert g.score_manager.score == game.Game.SCORE_PER_ENEMY

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_enemy_bullet_hits_player(self, mock_select, mock_exists):
        """测试敌人子弹击中玩家：玩家扣血"""
        g = game.Game()
        g.reset_game()
        g.player.invincible = False
        g.player.lives = 3
        # 敌人子弹方向1（向下），update会先移动子弹到玩家位置
        b = bullet.Bullet(g.player.x, g.player.y - 1, 1)
        g.enemy_group.bullets.append(b)
        g._update()
        assert g.player.lives == 2

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_enemy_bullet_hits_player_game_over(self, mock_select, mock_exists):
        """测试敌人子弹击中玩家且生命为0时进入 GAME_OVER"""
        g = game.Game()
        g.reset_game()
        g.player.invincible = False
        g.player.lives = 1
        b = bullet.Bullet(g.player.x, g.player.y - 1, 1)
        g.enemy_group.bullets.append(b)
        g._update()
        assert g.state == 'GAME_OVER'

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_enemy_reaches_bottom_game_over(self, mock_select, mock_exists):
        """测试敌人到达底部时进入 GAME_OVER"""
        g = game.Game()
        g.reset_game()
        for e in g.enemy_group.enemies:
            e.y = g.BOARD_HEIGHT - 1
        g._update()
        assert g.state == 'GAME_OVER'


# ============================================================
# 关卡推进测试
# ============================================================

class TestLevelProgression:
    """关卡推进测试"""

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_wave_clear_level_up(self, mock_select, mock_exists):
        """测试清空所有敌人后关卡提升"""
        g = game.Game()
        g.reset_game()
        initial_level = g.level
        # 消灭所有敌人
        for e in g.enemy_group.enemies:
            e.active = False
        g._update()
        assert g.level == initial_level + 1
        # 新波次应生成新敌人
        assert g.enemy_group.get_count() > 0

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_wave_clear_increases_difficulty(self, mock_select, mock_exists):
        """测试清空敌人后新波次难度增加（速度变快）"""
        g = game.Game()
        g.reset_game()
        old_speed = g.enemy_group.speed
        for e in g.enemy_group.enemies:
            e.active = False
        g._update()
        assert g.enemy_group.speed < old_speed


# ============================================================
# 边界情况测试
# ============================================================

class TestEdgeCases:
    """边界情况测试"""

    @patch('score_manager.os.path.exists', return_value=False)
    @patch('game.select.select', return_value=([], [], []))
    def test_update_does_nothing_when_not_playing(self, mock_select, mock_exists):
        """测试非 PLAYING 状态下 _update 不执行游戏逻辑"""
        g = game.Game()
        assert g.state == 'TITLE'
        old_player_x = g.player.x
        g._update()
        # 玩家位置不应变化
        assert g.player.x == old_player_x

    def test_bullet_repr(self):
        """测试 Bullet.__repr__ 输出格式"""
        b = bullet.Bullet(3, 7, -1)
        assert "Bullet(x=3, y=7" in repr(b)

    def test_player_repr(self):
        """测试 Player.__repr__ 输出格式"""
        p = player.Player(30, 20)
        assert "Player(x=" in repr(p)

    def test_enemy_repr(self):
        """测试 Enemy.__repr__ 输出格式"""
        e = enemy.Enemy(5, 5)
        assert "Enemy(x=5, y=5" in repr(e)

    def test_enemy_group_repr(self):
        """测试 EnemyGroup.__repr__ 输出格式"""
        eg = enemy.EnemyGroup(30, 20, rows=2, cols=3)
        assert "EnemyGroup(enemies=6" in repr(eg)

    def test_score_manager_repr(self):
        """测试 ScoreManager.__repr__ 输出格式"""
        sm = score_manager.ScoreManager("test_scores.json")
        assert "ScoreManager(score=0" in repr(sm)

    def test_sound_manager_repr(self):
        """测试 SoundManager.__repr__ 输出格式"""
        sm = sound_manager.SoundManager()
        assert "SoundManager(enabled=True" in repr(sm)

# 飞机大战 (Space Invaders)

一个基于控制台的太空侵略者小游戏，使用纯 Python 标准库开发。

## 游戏截图

```
      ╔══════════════════════════╗
      ║     ✈ 飞 机 大 战  ✈    ║
      ║     Space Invaders       ║
      ╚══════════════════════════╝
```

## 功能特性

- 🎮 **经典玩法**：控制飞船消灭入侵的敌人编队
- ❤️ **生命系统**：3 条命，被击中后短暂无敌闪烁
- 📊 **积分系统**：每次击杀 100 分，保存历史最高分
- 🏆 **最高分榜**：持久化存储 TOP 5 最高分
- 🔊 **音效系统**：使用 ASCII 响铃字符生成音效，可按 S 开关
- 📈 **难度递增**：每波敌人增多、速度加快，挑战性逐渐提升
- ⏸️ **暂停功能**：按 P 暂停/继续游戏
- ✨ **无敌闪烁**：重生后短暂无敌，闪烁提示

## 操作说明

| 按键 | 功能 |
|------|------|
| A / D | 左右移动飞船 |
| W / 空格 | 射击 |
| P | 暂停/继续 |
| S | 音效开关 |
| R | 游戏结束后重新开始 |
| Q | 退出游戏 |

## 技术栈

- **语言**: Python 3 (仅标准库)
- **界面**: 终端控制台 (ASCII 字符)
- **测试**: pytest
- **存储**: JSON 文件 (最高分)

## 项目结构

```
space-invaders/
├── game.py             # 主游戏类，游戏循环、渲染、输入处理
├── player.py           # 玩家飞船类
├── enemy.py            # 敌人和敌人编队类
├── bullet.py           # 子弹类
├── score_manager.py    # 分数管理（含持久化）
├── sound_manager.py    # 音效管理
├── scores.json         # 最高分数据文件（自动生成）
├── tests/
│   └── test_game.py    # 单元测试（77 个测试用例）
└── README.md           # 项目说明文档
```

## 快速开始

```bash
cd ~/games/space-invaders
python3 game.py
```

## 运行测试

```bash
cd ~/games/space-invaders
python3 -m pytest tests/ -v
```

## 测试覆盖

全部 **77 个测试用例**，覆盖以下模块：

- **Bullet**: 子弹创建、移动、边界检测
- **Player**: 移动、射击、受伤、无敌状态
- **Enemy/EnemyGroup**: 生成、移动、射击、编队行为
- **ScoreManager**: 计分、最高分判断、持久化
- **SoundManager**: 开关控制、各音效播放
- **Game**: 状态转换、输入处理、碰撞检测、关卡递进
- **边界情况**: 代表字符串、空状态等

## 游戏说明

1. 启动后进入标题画面，按任意键开始游戏
2. 控制飞船左右移动，射击消灭所有敌人通过当前波次
3. 敌人会左右移动并逐渐下移，同时随机发射子弹
4. 每清除一波敌人进入下一关，敌人增多、速度加快
5. 被敌人子弹击中扣除一条命，3 条命用完后游戏结束
6. 如果分数进入前 5 名，将记录到最高分榜

---

## Space Invaders

A console-based Space Invaders game built with pure Python standard library.

### Quick Start

```bash
cd ~/games/space-invaders
python3 game.py
```

### Controls

| Key | Action |
|-----|--------|
| A / D | Move left/right |
| W / Space | Shoot |
| P | Pause/Resume |
| S | Toggle sound |
| R | Restart (game over) |
| Q | Quit |

### Run Tests

```bash
cd ~/games/space-invaders
python3 -m pytest tests/ -v
```

All 77 test cases pass.

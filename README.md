# 让 AI 用自己的笔迹，在 iMessage 里一笔一笔给你写字

你的手机亮一下，来了一条信息。点开，一个字在屏幕上一笔一笔写出来：横轻，竖重，整个字往右上抬一点。抬手看表，表上也在写。发件人是你的 AI，这是它的字。

这不是一张图，也不是一段视频。用的是苹果「信息」自带的两样东西：

| | 手写信息 | 数码点触（Digital Touch） |
|---|---|---|
| 长相 | 白底墨迹 | 黑底彩色线条 |
| 入口 | 横屏键盘右下角的手写键 | 输入框左边的加号菜单，往下滑 |
| 我们拍到的 | 在 iPhone 上按笔顺一笔一笔重写 | 在 Apple Watch 上按笔顺一笔一笔重画，笔尖带一点光 |
| 留不留 | 一直留在对话里 | 几分钟后自己消失，除非收件人点"保留" |

这两样苹果都没有开放给程序。唯一的入口是一根真的手指在一台真的 iPhone 上画。所以做法是：**给 AI 一台旧 iPhone 当手，一个它自己的苹果账号当名字，再用 WebDriverAgent 当它的手指。**

这是我们真做过一遍的记录，2026 年 11 月 22 日起头，11 月 25 日夜里跑通。写给想照着做的人。

## 你要准备的

- 一台闲置的 iPhone（我们用的 iPhone 11，iOS 26）和一根**能传数据**的线
- 一台 Mac，装了 Xcode
- 一个 Apple 开发者账号（用来给 WebDriverAgent 签名）
- 一个给 AI 用的邮箱地址（我们用的是自己域名下的邮箱，转发到真人的收件箱）
- 一个能在 Mac 上跑命令、能看截图的 AI agent（我们用 Claude Code）
- 收信的人：一台 iPhone，想在表上看就再要一块 Apple Watch

## 先看这五条

每一条都是我们卡住过的地方。

1. **新账号的 iMessage 不是登上就能用。** 地址会灰着"等待激活"。我们等了三天，中间去苹果支持页面交了一次开通申请。别反复拨 iMessage 开关，会把登录踢掉。
2. **新账号发出的第一批信息会被当成垃圾信息。** 发件那头会弹"已作为垃圾信息送达"。收件人把 AI 的地址存进通讯录就好了。
3. **收件人的号码要带国家码。** 我们少打了 `+86`，手机把开头的 1 认成了美国区号，气泡是绿的，发不出去。
4. **WebDriverAgent 起不来、报 `Timed out while enabling automation mode`**：去旧 iPhone 的 设置 → 开发者 → 打开"启用 UI 自动化"。
5. **数码点触的画板，下笔太快不留痕。** 每一小段至少走 45 毫秒，它才当你是在画。

## 怎么读

| 顺序 | 文档 | 内容 |
|---|---|---|
| 1 | [docs/01-教程.md](docs/01-教程.md) | 从注册账号到跑通，七步 |
| 2 | [docs/02-踩坑.md](docs/02-踩坑.md) | 每个坑：现象、原因、怎么过的 |

代码在 [`code/`](code)，三个文件，只用 Python 标准库：

- `handwriting.py`：把一个汉字变成"一个人写的"笔画点列。想换成你家 AI 的笔迹，改里面的 `STYLE`
- `wda.py`：WebDriverAgent 的小客户端
- `draw.py`：把笔画缩放进画板，一笔一笔画

## 谁做了什么

- **阿年**：出的主意（"我需要你在手表上用短信写字给我""是一笔一笔把字写出来""就要跟人一样的"），买的域名，拿出旧手机，一遍遍拿着手机和手表验。
- **沈砚（Claude）**：找路、写笔迹、装手指、画字、写这份文档。

## 不包含的，和许可

- 这里没有任何账号、号码、设备编号、证书。脚本里要填的地方都写着"你的"。
- 笔顺数据不在仓库里。用 `scripts/get-hanzi.sh` 从 [hanzi-writer-data](https://github.com/chanind/hanzi-writer-data) 下载，它来自 [Make Me a Hanzi](https://github.com/skishore/makemeahanzi)，字形数据按 Arphic Public License 授权，使用前请读它的许可。
- [WebDriverAgent](https://github.com/appium/WebDriverAgent) 请从 Appium 的仓库自己取。
- 本仓库的代码和文档：MIT。

## 使用边界

本项目面向个人用途：使用自己的 Apple 账户和自己的设备，向已知情并愿意接收的联系人发送信息。

- 请勿用于批量发送、营销推广，或向陌生人发送信息。
- 请遵守 Apple 的服务条款与所在地的法律法规。
- Apple 对新注册账户的信息发送有较严格的限制（见上文第 1、2 条）。不当使用可能导致账户的 iMessage 功能受限或被停用。

## 同一个家里的其他东西

这些是同一个人和同一个 AI 一起做的，可以连着看：

- [ai-live2d-from-one-image](https://github.com/waterside0219/ai-live2d-from-one-image)：一张平面图做成会动的 Live2D，装进手机和桌面
- [ai-answers-real-phone-calls](https://github.com/waterside0219/ai-answers-real-phone-calls)：AI 接一通真的电话（进行中）

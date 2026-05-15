## 问道多开窗口自动化（MVP）

### 你将得到什么

- 绑定并管理 **5 个问道客户端窗口**
- 轮询每个窗口，执行：
  - 聚焦窗口（前台）
  - 在窗口内点击（相对坐标）
  - 截图指定区域
  - OCR 读取对话/任务提示文本（Tesseract）

> 说明：很多端游窗口（尤其是 DX/反作弊/输入钩子）对“后台点击”不友好，本 MVP 采用 **前台聚焦后再点击** 的方式，稳定性最好。

### 免责声明（务必阅读）

该项目仅用于学习 Windows 自动化与图像识别。请遵守游戏用户协议与当地法律法规；任何账号风险由使用者自行承担。

### 环境要求

- Windows 10/11
- Python 3.10+（建议 3.11）
- OCR 默认 `auto`：优先使用 RapidOCR（无需额外 exe），其次才是 Tesseract

### 安装依赖

在仓库根目录打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r wenda-bot\requirements.txt
```

### 首次配置

编辑 `wenda-bot/config.json`：

- `windows[i].title_regex`：每个客户端窗口标题的正则（推荐用 “角色名/区组名” 匹配）
- `ocr.backend`：`auto` / `rapidocr` / `tesseract`
- `ocr.tesseract_cmd`：仅当你使用 tesseract 时需要
- `regions.dialog` / `regions.quest_hint`：对话框与任务提示所在区域（相对窗口客户区坐标）
- `clicks.*`：NPC、对话选项、怪物、自动战斗按钮等相对坐标（先填你抓到的点位）

### 运行

```powershell
python -m wenda_bot.main
```

运行时会打印每个窗口的 OCR 结果（对话/任务提示），并按状态机尝试点击。

### GUI 界面运行（推荐）

```powershell
python -m wenda_bot.gui
```

界面包含：

- `Refresh Windows`：刷新并显示 5 个客户端窗口绑定结果
- `Start Bot` / `Stop Bot`：启动或停止自动流程
- `Click Point Calibration`：选择客户端槽位和目标点，按 `Start Capture` 后将鼠标移到目标位置，按 `F8` 采点并自动保存到 `config.json`
- `Runtime Logs`：查看 OCR 文本、点击执行与错误信息

### 打包成 EXE（PyInstaller）

```powershell
pip install pyinstaller
pyinstaller -F -n wenda-bot wenda-bot\wenda_bot\main.py
```

生成的 exe 在 `dist/` 下。


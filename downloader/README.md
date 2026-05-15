## downloader

一个支持**多线程分片**与**断点续传**的下载脚本（Windows 也可用）。

### 用法

下载你给的 PyTorch wheel（默认 16 路并发）：

```bash
python downloader/download.py "https://download-r2.pytorch.org/whl/cu124/torch-2.6.0%2Bcu124-cp312-cp312-win_amd64.whl"
```

指定输出路径与并发数：

```bash
python downloader/download.py "URL" -o "D:\Downloads\torch.whl" -c 32
```

### 断点续传说明

- 会在输出文件同级目录创建一个隐藏分片目录：`.{输出文件名}.parts/`
- 中断后再次运行同一条命令，会自动从每个 `partXXX` 的已有大小继续下载
- 全部分片校验通过后合并为最终文件；合并时会先写入 `*.downloading`，最后原子替换


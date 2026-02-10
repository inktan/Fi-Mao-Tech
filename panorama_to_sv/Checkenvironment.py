#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境检查工具 - 检测CUDA和OpenCV配置
"""

import sys
import subprocess

def check_opencv():
    """检查OpenCV"""
    print("\n" + "=" * 70)
    print("OpenCV检查")
    print("=" * 70)
    
    try:
        import cv2
        print(f"✅ OpenCV已安装")
        print(f"   版本: {cv2.__version__}")
        print(f"   路径: {cv2.__file__}")
        
        # 检查编译信息
        build_info = cv2.getBuildInformation()
        
        # 查找CUDA相关信息
        cuda_found = False
        for line in build_info.split('\n'):
            if 'CUDA' in line or 'cuDNN' in line:
                print(f"   {line.strip()}")
                if 'YES' in line or 'CUDA:' in line:
                    cuda_found = True
        
        # 检查CUDA设备
        print(f"\n   CUDA模块检查:")
        try:
            count = cv2.cuda.getCudaEnabledDeviceCount()
            if count > 0:
                print(f"   ✅ CUDA设备数量: {count}")
                for i in range(count):
                    print(f"      设备 {i}: 可用")
            else:
                print(f"   ⚠️  未检测到CUDA设备")
                print(f"      可能原因:")
                print(f"      1. OpenCV未编译CUDA支持")
                print(f"      2. 没有NVIDIA GPU")
                print(f"      3. CUDA驱动未安装")
        except AttributeError:
            print(f"   ❌ cv2.cuda 模块不存在")
            print(f"      原因: OpenCV编译时未启用CUDA")
        except Exception as e:
            print(f"   ❌ CUDA检测失败: {e}")
        
        return True
        
    except ImportError:
        print(f"❌ OpenCV未安装")
        print(f"   安装命令: pip install opencv-python")
        return False


def check_cuda_toolkit():
    """检查CUDA Toolkit"""
    print("\n" + "=" * 70)
    print("CUDA Toolkit检查")
    print("=" * 70)
    
    try:
        result = subprocess.run(['nvcc', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # 提取版本信息
            output = result.stdout
            for line in output.split('\n'):
                if 'release' in line.lower():
                    print(f"✅ CUDA Toolkit已安装")
                    print(f"   {line.strip()}")
                    
                    # 提取版本号
                    if 'release ' in line:
                        version = line.split('release ')[1].split(',')[0]
                        major = version.split('.')[0]
                        print(f"\n   版本: CUDA {version}")
                        print(f"   主版本: {major}")
                        
                        # 推荐CuPy版本
                        if major == '11':
                            print(f"   推荐CuPy: pip install cupy-cuda11x")
                        elif major == '12':
                            print(f"   推荐CuPy: pip install cupy-cuda12x")
                    break
            return True
        else:
            print(f"❌ nvcc命令执行失败")
            return False
            
    except FileNotFoundError:
        print(f"❌ CUDA Toolkit未安装（nvcc未找到）")
        print(f"   下载地址: https://developer.nvidia.com/cuda-downloads")
        return False
    except Exception as e:
        print(f"❌ CUDA检测失败: {e}")
        return False


def check_nvidia_gpu():
    """检查NVIDIA GPU"""
    print("\n" + "=" * 70)
    print("NVIDIA GPU检查")
    print("=" * 70)
    
    try:
        result = subprocess.run(['nvidia-smi'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ NVIDIA GPU已检测到")
            
            # 解析nvidia-smi输出
            lines = result.stdout.split('\n')
            
            # 查找驱动版本
            for line in lines:
                if 'Driver Version' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        driver_info = parts[1].strip()
                        print(f"   驱动版本: {driver_info}")
                        break
            
            # 查找GPU信息
            print(f"\n   GPU列表:")
            in_gpu_section = False
            for line in lines:
                if '|' in line and ('MiB' in line or 'Default' in line):
                    in_gpu_section = True
                if in_gpu_section and '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 2 and any(char.isdigit() for char in parts[1]):
                        gpu_info = ' '.join(parts[1:4])
                        if gpu_info.strip():
                            print(f"   {gpu_info}")
                if in_gpu_section and '===' in line:
                    break
            
            return True
        else:
            print(f"❌ nvidia-smi执行失败")
            return False
            
    except FileNotFoundError:
        print(f"❌ nvidia-smi未找到")
        print(f"   可能原因:")
        print(f"   1. 未安装NVIDIA驱动")
        print(f"   2. 没有NVIDIA GPU")
        print(f"   下载驱动: https://www.nvidia.com/drivers")
        return False
    except Exception as e:
        print(f"❌ GPU检测失败: {e}")
        return False


def check_cupy():
    """检查CuPy"""
    print("\n" + "=" * 70)
    print("CuPy检查")
    print("=" * 70)
    
    try:
        import cupy as cp
        print(f"✅ CuPy已安装")
        print(f"   版本: {cp.__version__}")
        
        # CUDA运行时版本
        try:
            cuda_version = cp.cuda.runtime.runtimeGetVersion()
            major = cuda_version // 1000
            minor = (cuda_version % 1000) // 10
            print(f"   CUDA运行时: {major}.{minor}")
        except:
            pass
        
        # 设备信息
        try:
            device_count = cp.cuda.runtime.getDeviceCount()
            print(f"   CUDA设备: {device_count}")
            
            for i in range(device_count):
                props = cp.cuda.runtime.getDeviceProperties(i)
                name = props['name'].decode('utf-8')
                mem = props['totalGlobalMem'] / (1024**3)
                print(f"      设备 {i}: {name} ({mem:.1f} GB)")
        except Exception as e:
            print(f"   设备信息获取失败: {e}")
        
        return True
        
    except ImportError:
        print(f"❌ CuPy未安装")
        print(f"\n   安装建议:")
        print(f"   CUDA 11.x: pip install cupy-cuda11x")
        print(f"   CUDA 12.x: pip install cupy-cuda12x")
        return False


def check_python():
    """检查Python环境"""
    print("\n" + "=" * 70)
    print("Python环境")
    print("=" * 70)
    
    print(f"✅ Python版本: {sys.version}")
    print(f"   可执行文件: {sys.executable}")
    
    # 检查必要的包
    packages = {
        'numpy': 'NumPy',
        'PIL': 'Pillow',
        'tqdm': 'tqdm'
    }
    
    print(f"\n   依赖包:")
    all_installed = True
    for module, name in packages.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', '未知版本')
            print(f"   ✅ {name}: {version}")
        except ImportError:
            print(f"   ❌ {name}: 未安装")
            all_installed = False
    
    if not all_installed:
        print(f"\n   安装缺失的包:")
        print(f"   pip install numpy pillow tqdm opencv-python")
    
    return all_installed


def recommend_solution():
    """推荐解决方案"""
    print("\n" + "=" * 70)
    print("💡 推荐方案")
    print("=" * 70)
    
    has_opencv = False
    has_cuda_opencv = False
    has_cupy = False
    has_gpu = False
    
    # 检查OpenCV
    try:
        import cv2
        has_opencv = True
        try:
            count = cv2.cuda.getCudaEnabledDeviceCount()
            if count > 0:
                has_cuda_opencv = True
        except:
            pass
    except:
        pass
    
    # 检查CuPy
    try:
        import cupy
        has_cupy = True
    except:
        pass
    
    # 检查GPU
    try:
        result = subprocess.run(['nvidia-smi'], 
                              capture_output=True, timeout=2)
        if result.returncode == 0:
            has_gpu = True
    except:
        pass
    
    print()
    
    if has_cuda_opencv:
        print("🚀 方案1: 使用GPU加速版本（最快）")
        print("   文件: panorama_gpu.py")
        print("   预期提速: 10-20倍")
        print("   ✅ OpenCV CUDA支持已启用")
        print()
        
    if has_cupy and has_gpu:
        print("⚡ 方案2: 使用CuPy辅助的CPU版本")
        print("   文件: panorama_optimizer.py")
        print("   设置: use_gpu=True")
        print("   预期提速: 6-8倍")
        print("   ✅ CuPy可用")
        print()
    
    if has_opencv:
        print("✅ 方案3: 使用多核CPU版本（推荐）")
        print("   文件: panorama_enhanced.py")
        print("   预期提速: 4-8倍")
        print("   优点: 稳定可靠，无需GPU")
        print()
    
    if not has_opencv:
        print("❌ 请先安装OpenCV:")
        print("   pip install opencv-python numpy pillow tqdm")
        print()
    
    # 具体建议
    print("\n📋 具体建议:")
    
    if not has_opencv:
        print("1. 安装基础依赖:")
        print("   pip install opencv-python numpy pillow tqdm")
    elif not has_gpu:
        print("1. 您没有NVIDIA GPU，建议使用:")
        print("   python panorama_enhanced.py")
        print("   （多核CPU版本，已经很快了）")
    elif not has_cuda_opencv and not has_cupy:
        print("1. 有GPU但CUDA支持未配置，两个选择:")
        print()
        print("   选择A（简单）: 安装CuPy")
        print("   pip install cupy-cuda11x  # 或cuda12x")
        print("   然后运行: python panorama_optimizer.py")
        print()
        print("   选择B（复杂）: 编译支持CUDA的OpenCV")
        print("   参考: CUDA问题解决方案.md")
        print("   然后运行: python panorama_gpu.py")
        print()
        print("   推荐选择A（更简单，效果也不错）")
    else:
        print("1. 您的环境配置完善！")
        if has_cuda_opencv:
            print("   推荐: python panorama_gpu.py（最快）")
        elif has_cupy:
            print("   推荐: python panorama_optimizer.py (use_gpu=True)")


def main():
    """主函数"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "环境检查工具" + " " * 36 + "║")
    print("║" + " " * 14 + "全景图转街景图 - CUDA配置检测" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # 执行各项检查
    check_python()
    check_nvidia_gpu()
    check_cuda_toolkit()
    check_opencv()
    check_cupy()
    
    # 推荐方案
    recommend_solution()
    
    print("\n" + "=" * 70)
    print("检查完成！")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
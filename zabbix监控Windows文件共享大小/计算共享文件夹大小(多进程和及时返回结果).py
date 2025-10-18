import json
import multiprocessing
import os
import random
import shutil
import subprocess
import time


# 获取文件夹的大小
def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                continue  # 忽略无法访问的文件
    return total_size

def get_smb_shares():
    # 调用powershell命令获取文件共享的名称和路径
    ps_command = r"""
    Get-SmbShare -ErrorAction Stop | 
    Where-Object { 
        (-not $_.Name.Endswith('$')) -and 
        ($_.Name -notin @('ADMIN$', 'IPC$', 'PRINT$')) 
    } | 
    Select-Object Name, Path | 
    ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)
    return json.loads(result.stdout)

# 处理单个共享文件夹的任务函数
def process_share(share):
    # delay = random.randint(10, 120)
    # time.sleep(delay)
    try:
        size = get_directory_size(share['Path'])
        size_mb = size / (1024 ** 2)
        return (share['Name'], round(size_mb,2))
    except Exception as e:
        return (share['Name'], f"Error: {str(e)}")

# 回调函数，用于处理每个任务完成后的结果
def write_result(result, txtfile):
    name, size = result
    # 将结果格式化为字符串并写入文本文件
    txtfile.write(f"{name}: {size}\n")
    txtfile.flush()  # 确保立即写入文件

def main():
    try:
        shares = get_smb_shares()
    except subprocess.CalledProcessError as e:
        print(f"Powershell命令执行失败:{e.stderr}")
        return
    except json.JSONDecodeError:
        print("解析失败")
        return
    except Exception as e:
        print(str(e))
        return

    # 打开文本文件准备写入
    with open("temp.txt", "w", encoding='utf-8') as txtfile:
        # 创建进程池
        with multiprocessing.Pool() as pool:
            # 为每个共享创建一个异步任务，并指定回调函数
            for share in shares:
                pool.apply_async(
                    process_share,
                    args=(share,),
                    callback=lambda res: write_result(res, txtfile)
                )
            # 等待所有任务完成
            pool.close()
            pool.join()

if __name__ == "__main__":
    # 确保在Windows上正确使用多进程
    multiprocessing.freeze_support()
    main()
    # 将临时文件复制为最后结果文件
    temp_file = 'temp.txt'
    result_file = 'shares_size.txt'
    try:
        shutil.copy(temp_file, result_file)
    except FileNotFoundError:
        print('临时文件不存')
    except PermissionError:
        print('没有足够的权限进行文件复制')
    except Exception as e:
        print(f'发生未知错误: {e}')
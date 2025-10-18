import json
import multiprocessing
import os
import subprocess
import csv


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
    # 转为GB,保留4位有效
    # total_size = round(total_size/1024/1024/1024, 4)
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
    try:
        size = get_directory_size(share['Path'])
        return (share['Name'], size)
    except Exception as e:
        return (share['Name'], f"Error: {str(e)}")


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

    # 创建进程池
    with multiprocessing.Pool() as pool:
        # 使用map_async异步处理所有共享
        results = pool.map_async(process_share, shares)
        # 等待所有进程完成
        results.wait()
        # 获取结果列表
        share_results = results.get()

    # 将结果写入CSV文件
    with open("pdm.csv", "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for name, size in share_results:
            writer.writerow([name, size])


if __name__ == "__main__":
    # 确保在Windows上正确使用多进程
    multiprocessing.freeze_support()
    main()

# def main():
#     try:
#         shares = get_smb_shares()
#     except subprocess.CalledProcessError as e:
#         print(f"Powershell命令执行失败:{e.stderr}")
#         return
#     except json.JSONDecodeError:
#         print("解析失败")
#         return
#     except Exception as e:
#         print(str(e))
#         return
#     with open("pdm.csv", "w", newline='', encoding='utf-8') as csvfile:
#         writer = csv.writer(csvfile)
#         for share in shares:
#             # 计算共享文件夹的大小
#             # 将结果写入csv文件
#             try:
#                 size = get_directory_size(share['Path'])
#                 writer.writerow([share['Name'], size])
#             except Exception as e:
#                 print(f"处理共享 '{share['Name']}' 时出错: {str(e)}")
#
#
# if __name__ == "__main__":
#     main()

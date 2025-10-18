import argparse
import os
import sys


def match_number_from_file(query):
    """
    从文件中读取内容，根据查询字符串匹配对应的数字
    :param query: 要匹配的字符串，如"基础平台部"
    :param file_path: 文件路径
    :return: 匹配到的数字字符串（如"108.46"），如果没有匹配则返回None
    """
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建完整文件路径
    file_path = os.path.join(script_dir, 'shares_size.txt')
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 处理内容并匹配
        lines = content.splitlines()
        for line in lines:
            if query in line:
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    return parts[1].strip()
        return None

    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到", file=sys.stderr)
        return None
    except Exception as e:
        print(f"读取文件时出错: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='从文件中查找匹配查询字符串的数字')
    parser.add_argument('query', type=str, help='要匹配的字符串')
    # parser.add_argument('file_path', type=str, help='文件路径')

    args = parser.parse_args()

    # 调用匹配函数
    result = match_number_from_file(args.query)

    # 输出结果（仅打印匹配结果，错误信息已在函数内打印）
    if result is not None:
        print(result)
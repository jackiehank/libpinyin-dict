#!/usr/bin/env python3
"""
中文分词处理脚本
功能：对指定文件或目录中的文本文件进行中文分词，过滤非中文内容，并导出为去重的词汇列表
修改：目录处理时合并所有文件结果到单个文件
"""

import argparse
import os
import sys
import re
import jieba
from pathlib import Path
from collections import defaultdict

def init_jieba():
    """初始化jieba分词器"""
    # 启用并行分词，提高速度
    jieba.enable_parallel(4)
    # 关闭调试输出
    jieba.setLogLevel(20)  # 避免INFO级别的日志

def is_chinese_word(word):
    """
    检查词汇是否为纯中文
    使用正则表达式匹配中文字符（包括基本汉字和扩展汉字区域）
    """
    # 匹配中文字符，包括基本汉字(4E00-9FFF)和扩展汉字区域(3400-4DBF, 20000-2A6DF等)
    chinese_pattern = re.compile(r'^[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df]+$')
    return bool(chinese_pattern.match(word))

def ensure_output_dir(output_path):
    """确保输出目录存在"""
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

def get_unique_output_path(output_dir, base_filename):
    """
    生成唯一的输出文件路径，避免覆盖现有文件
    """
    output_dir = Path(output_dir)
    base_name = Path(base_filename).stem
    extension = ".txt"
    
    # 初始尝试使用基本文件名
    output_path = output_dir / f"{base_name}_segmented{extension}"
    
    # 如果文件已存在，添加数字后缀
    counter = 1
    while output_path.exists():
        output_path = output_dir / f"{base_name}_segmented_{counter}{extension}"
        counter += 1
    
    return output_path

def extract_chinese_words(content):
    """
    从内容中提取中文词汇并去重
    """
    if not content:
        return set()
    
    # 使用jieba进行中文分词
    words = jieba.cut(content)
    
    # 过滤非中文词汇并去重
    unique_words = set()
    for word in words:
        word = word.strip()
        # 过滤空字符串和非中文词汇
        if word and is_chinese_word(word):
            unique_words.add(word)
    
    return unique_words

def process_file(file_path, output_dir="raw"):
    """
    处理单个文件：读取、分词、过滤非中文、去重
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"警告: 文件 {file_path} 为空，跳过处理")
            return None
        
        # 提取中文词汇
        unique_words = extract_chinese_words(content)
        
        if not unique_words:
            print(f"警告: 文件 {file_path} 没有有效的中文词汇，跳过处理")
            return None
        
        # 确保输出目录存在
        output_dir_path = ensure_output_dir(output_dir)
        
        # 生成唯一的输出文件名
        input_path = Path(file_path)
        output_path = get_unique_output_path(output_dir, input_path.name)
        
        # 写入结果
        with open(output_path, 'w', encoding='utf-8') as f:
            for word in sorted(unique_words):  # 按Unicode顺序排序
                f.write(word + '\n')
        
        print(f"成功处理: {file_path} -> {output_path}")
        print(f"  提取中文词汇数: {len(unique_words)}")
        
        return output_path, len(unique_words), unique_words
        
    except UnicodeDecodeError:
        print(f"错误: 文件 {file_path} 编码不是UTF-8，请检查文件编码")
        return None
    except Exception as e:
        print(f"错误: 处理文件 {file_path} 时发生异常: {str(e)}")
        return None

def process_directory(directory_path, output_dir="raw", recursive=False, merge_output=True):
    """
    处理目录中的所有文本文件
    merge_output: 是否合并输出到单个文件
    """
    directory_path = Path(directory_path)
    text_files = []
    
    # 支持多种文本文件格式
    extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm']
    
    # 收集文本文件
    if recursive:
        for ext in extensions:
            text_files.extend(directory_path.glob(f"**/*{ext}"))
    else:
        for ext in extensions:
            text_files.extend(directory_path.glob(f"*{ext}"))
    
    # 去重并确保是文件
    text_files = list(set([f for f in text_files if f.is_file()]))
    
    if not text_files:
        print(f"警告: 在目录 {directory_path} 中未找到支持的文本文件")
        return []
    
    print(f"找到 {len(text_files)} 个文本文件")
    
    # 确保输出目录存在
    ensure_output_dir(output_dir)
    
    if merge_output:
        # 合并模式：将所有文件的分词结果合并到一个文件
        return process_directory_merged(directory_path, text_files, output_dir)
    else:
        # 分散模式：每个文件单独输出
        return process_directory_separate(text_files, output_dir)

def process_directory_merged(directory_path, text_files, output_dir):
    """
    处理目录并将所有结果合并到单个文件
    """
    all_unique_words = set()
    processed_files = {}
    successful_files = 0
    
    print("启用合并输出模式...")
    
    for file_path in text_files:
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                print(f"警告: 文件 {file_path} 为空，跳过处理")
                continue
            
            # 提取中文词汇
            unique_words = extract_chinese_words(content)
            
            if not unique_words:
                print(f"警告: 文件 {file_path} 没有有效的中文词汇，跳过处理")
                continue
            
            # 合并到总集合中
            all_unique_words.update(unique_words)
            successful_files += 1
            
            print(f"处理完成: {file_path} (词汇数: {len(unique_words)})")
            
            # 跟踪重名文件
            filename = file_path.name
            processed_files[filename] = processed_files.get(filename, 0) + 1
            
        except UnicodeDecodeError:
            print(f"错误: 文件 {file_path} 编码不是UTF-8，跳过处理")
        except Exception as e:
            print(f"错误: 处理文件 {file_path} 时发生异常: {str(e)}")
    
    if not all_unique_words:
        print("错误: 没有成功提取任何中文词汇")
        return []
    
    # 生成合并输出文件名
    dir_name = directory_path.name
    output_filename = f"{dir_name}_merged_segmented.txt"
    output_path = Path(output_dir) / output_filename
    
    # 如果文件已存在，添加数字后缀
    counter = 1
    while output_path.exists():
        output_path = Path(output_dir) / f"{dir_name}_merged_segmented_{counter}.txt"
        counter += 1
    
    # 写入合并结果
    with open(output_path, 'w', encoding='utf-8') as f:
        for word in sorted(all_unique_words):  # 按Unicode顺序排序
            f.write(word + '\n')
    
    print(f"\n合并处理完成！")
    print(f"成功处理文件数: {successful_files}/{len(text_files)}")
    print(f"合并去重后总词汇数: {len(all_unique_words)}")
    print(f"输出文件: {output_path}")
    
    # 输出重名文件统计
    duplicate_files = {name: count for name, count in processed_files.items() if count > 1}
    if duplicate_files:
        print(f"\n注意: 共发现 {len(duplicate_files)} 个重名文件，已合并处理:")
        for name, count in duplicate_files.items():
            print(f"  {name}: {count} 个版本")
    
    return [(output_path, len(all_unique_words), all_unique_words)]

def process_directory_separate(text_files, output_dir):
    """
    处理目录但每个文件单独输出（保留原功能）
    """
    results = []
    processed_files = {}  # 跟踪已处理的文件名，避免重复
    
    for file_path in text_files:
        # 检查是否已经处理过同名文件
        filename = file_path.name
        if filename in processed_files:
            print(f"注意: 发现重名文件 {file_path}，将使用不同文件名保存")
        
        result = process_file(file_path, output_dir)
        if result:
            results.append(result)
            processed_files[filename] = processed_files.get(filename, 0) + 1
    
    # 输出重名文件统计
    duplicate_files = {name: count for name, count in processed_files.items() if count > 1}
    if duplicate_files:
        print(f"\n注意: 共发现 {len(duplicate_files)} 个重名文件，已分别保存:")
        for name, count in duplicate_files.items():
            print(f"  {name}: {count} 个版本")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description="中文分词处理工具 - 对文本文件进行中文分词，过滤非中文内容，并导出去重词汇",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s document.txt                    # 处理单个文件，输出到raw/目录
  %(prog)s /path/to/documents/             # 处理目录，合并输出到单个文件
  %(prog)s input.txt -o custom_output/     # 指定输出目录
  %(prog)s docs/ -r -o results/            # 递归处理子目录，合并输出
  %(prog)s docs/ --no-merge               # 目录处理时不合并，每个文件单独输出
        """
    )
    
    parser.add_argument(
        'path',
        help='输入路径（文件或目录）'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default='raw',
        help='输出目录（默认：raw/）'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='递归处理子目录（仅当输入为目录时有效）'
    )
    
    parser.add_argument(
        '--no-merge',
        action='store_true',
        help='目录处理时不合并输出（默认合并）'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.1'
    )
    
    args = parser.parse_args()
    
    # 检查路径是否存在
    if not os.path.exists(args.path):
        print(f"错误: 路径 '{args.path}' 不存在")
        sys.exit(1)
    
    # 初始化jieba
    init_jieba()
    
    # 处理路径
    if os.path.isfile(args.path):
        # 处理单个文件
        print(f"开始处理文件: {args.path}")
        result = process_file(args.path, args.output_dir)
        if not result:
            sys.exit(1)
            
    elif os.path.isdir(args.path):
        # 处理目录
        print(f"开始处理目录: {args.path}")
        if args.recursive:
            print("启用递归模式")
        
        # 根据参数决定是否合并输出
        merge_output = not args.no_merge
        if merge_output:
            print("启用合并输出模式（所有结果将合并到一个文件）")
        else:
            print("启用分散输出模式（每个文件单独输出）")
        
        results = process_directory(args.path, args.output_dir, args.recursive, merge_output)
        
        if results:
            if merge_output:
                # 合并模式下只有一个结果
                output_path, total_words, _ = results[0]
                print(f"\n处理完成！共处理 {len(results)} 个合并文件，中文词汇数: {total_words}")
                print(f"结果已保存到: {output_path}")
            else:
                # 分散模式下有多个结果
                total_words = sum(count for _, count, _ in results)
                print(f"\n处理完成！共处理 {len(results)} 个文件，总计中文词汇数: {total_words}")
                print(f"所有结果已保存到: {args.output_dir}/")
        else:
            print("没有成功处理任何文件")
            sys.exit(1)
    else:
        print(f"错误: '{args.path}' 不是文件也不是目录")
        sys.exit(1)

if __name__ == "__main__":
    main()
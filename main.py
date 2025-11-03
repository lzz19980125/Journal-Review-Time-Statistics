import fitz  # PyMuPDF
import re
import os
import sys
from datetime import datetime
from pathlib import Path
from statistics import median

# 设置输出编码为UTF-8，避免Windows中文乱码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_text_from_pdf(pdf_path):
    """从PDF文件中提取文本内容"""
    try:
        doc = fitz.open(pdf_path)
        # 提取前几页的文本，日期信息通常在前面
        text = ""
        for page_num in range(min(3, len(doc))):  # 读取前3页
            text += doc[page_num].get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"读取PDF文件 {pdf_path} 时出错: {str(e)}")
        return None

def parse_date(date_string):
    """解析日期字符串，支持多种格式"""
    # 常见的日期格式
    date_formats = [
        r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
        r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
        r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',
        r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})'
    ]
    
    month_dict = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    for fmt in date_formats:
        match = re.search(fmt, date_string, re.IGNORECASE)
        if match:
            groups = match.groups()
            try:
                if len(groups) == 3:
                    # 检查第二个组是否是月份名称
                    if groups[1].lower() in month_dict:
                        day = int(groups[0])
                        month = month_dict[groups[1].lower()]
                        year = int(groups[2])
                        return datetime(year, month, day)
                    # 检查是否是纯数字格式
                    elif groups[0].isdigit() and groups[1].isdigit() and groups[2].isdigit():
                        # YYYY-MM-DD格式
                        if len(groups[0]) == 4:
                            return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                        # DD-MM-YYYY格式
                        else:
                            return datetime(int(groups[2]), int(groups[1]), int(groups[0]))
            except ValueError:
                continue
    
    return None

def extract_dates_from_text(text):
    """从文本中提取Received、Revised和Accepted日期
    兼容多种期刊格式：
    - Elsevier: "Received 8 April 2024; Received in revised form 23 August 2024; Accepted 15 September 2024"
    - IEEE: "Received 17 January 2025; revised 31 March 2025; accepted 24 April 2025"
    """
    dates = {
        'received': None,
        'revised': None,
        'accepted': None
    }
    
    if not text:
        return dates
    
    # 模式1: 尝试匹配Elsevier格式（Received in revised form）
    elsevier_pattern = r'Received\s+(\d{1,2}\s+\w+\s+\d{4}).*?revised\s+form\s+(\d{1,2}\s+\w+\s+\d{4}).*?Accepted\s+(\d{1,2}\s+\w+\s+\d{4})'
    match = re.search(elsevier_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        dates['received'] = parse_date(match.group(1))
        dates['revised'] = parse_date(match.group(2))
        dates['accepted'] = parse_date(match.group(3))
        return dates
    
    # 模式2: 尝试匹配IEEE格式（直接是revised）
    ieee_pattern = r'Received\s+(\d{1,2}\s+\w+\s+\d{4}).*?revised\s+(\d{1,2}\s+\w+\s+\d{4}).*?accepted\s+(\d{1,2}\s+\w+\s+\d{4})'
    match = re.search(ieee_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        dates['received'] = parse_date(match.group(1))
        dates['revised'] = parse_date(match.group(2))
        dates['accepted'] = parse_date(match.group(3))
        return dates
    
    # 如果上面的完整模式都没有匹配，尝试单独查找每个日期
    # 将文本按行分割并合并相邻行（因为日期信息可能跨行）
    lines = text.split('\n')
    
    # 在整个文本中搜索日期信息
    for i, line in enumerate(lines):
        # 合并当前行和下一行，以处理跨行的情况
        context = line + ' ' + (lines[i+1] if i+1 < len(lines) else '')
        context_lower = context.lower()
        
        # 查找Received日期（不包括"Received in revised form"）
        if 'received' in context_lower and dates['received'] is None:
            received_pattern = r'Received\s+(\d{1,2}\s+\w+\s+\d{4})'
            match = re.search(received_pattern, context, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # 确保这不是"Received in revised form"后面的日期
                before_match = context[:match.start()].lower()
                if 'revised' not in before_match and 'revision' not in before_match:
                    dates['received'] = parse_date(date_str)
        
        # 查找Revised日期 - 兼容两种格式
        if ('revised' in context_lower or 'revision' in context_lower) and dates['revised'] is None:
            # 优先匹配"Received in revised form [date]"格式
            revised_pattern1 = r'revised\s+form\s+(\d{1,2}\s+\w+\s+\d{4})'
            match = re.search(revised_pattern1, context, re.IGNORECASE)
            if match:
                dates['revised'] = parse_date(match.group(1))
            else:
                # 匹配"revised [date]"格式（IEEE）
                # 但要确保不是"revised form"
                revised_pattern2 = r'revised\s+(?!form)(\d{1,2}\s+\w+\s+\d{4})'
                match = re.search(revised_pattern2, context, re.IGNORECASE)
                if match:
                    dates['revised'] = parse_date(match.group(1))
        
        # 查找Accepted日期
        if 'accepted' in context_lower and dates['accepted'] is None:
            accepted_pattern = r'accepted\s+(\d{1,2}\s+\w+\s+\d{4})'
            match = re.search(accepted_pattern, context, re.IGNORECASE)
            if match:
                dates['accepted'] = parse_date(match.group(1))
    
    return dates

def calculate_days_difference(date1, date2):
    """计算两个日期之间的天数差"""
    if date1 and date2:
        return abs((date2 - date1).days)
    return None

def process_pdf_folder(folder_path):
    """处理文件夹中的所有PDF文件"""
    folder = Path(folder_path)
    pdf_files = list(folder.glob('*.pdf'))
    
    print(f"\n找到 {len(pdf_files)} 个PDF文件\n")
    print("=" * 80)
    
    results = []
    
    for pdf_file in pdf_files:
        print(f"\n处理文件: {pdf_file.name}")
        
        # 提取文本
        text = extract_text_from_pdf(str(pdf_file))
        if not text:
            print("  ⚠️  无法读取PDF文件")
            continue
        
        # 提取日期
        dates = extract_dates_from_text(text)
        
        # 显示提取的日期
        print(f"  Received: {dates['received'].strftime('%Y-%m-%d') if dates['received'] else '未找到'}")
        print(f"  Revised:  {dates['revised'].strftime('%Y-%m-%d') if dates['revised'] else '未找到'}")
        print(f"  Accepted: {dates['accepted'].strftime('%Y-%m-%d') if dates['accepted'] else '未找到'}")
        
        # 计算时间差
        received_to_revised = calculate_days_difference(dates['received'], dates['revised'])
        received_to_accepted = calculate_days_difference(dates['received'], dates['accepted'])
        
        if received_to_revised:
            months = received_to_revised / 30
            print(f"  >> Received -> Revised: {received_to_revised} 天 ({months:.1f} 个月)")
        if received_to_accepted:
            months = received_to_accepted / 30
            print(f"  >> Received -> Accepted: {received_to_accepted} 天 ({months:.1f} 个月)")
        
        # 保存结果
        results.append({
            'filename': pdf_file.name,
            'received': dates['received'],
            'revised': dates['revised'],
            'accepted': dates['accepted'],
            'received_to_revised': received_to_revised,
            'received_to_accepted': received_to_accepted
        })
        
        print("-" * 80)
    
    return results

def calculate_statistics(results, journal_name):
    """计算统计数据"""
    print("\n" + "=" * 80)
    print("【统计结果】")
    print("=" * 80)
    
    # 过滤出有效数据
    valid_received_to_revised = [r['received_to_revised'] for r in results if r['received_to_revised'] is not None]
    valid_received_to_accepted = [r['received_to_accepted'] for r in results if r['received_to_accepted'] is not None]
    
    print(f"\n处理{journal_name}的PDF文件总数: {len(results)}")
    print(f"成功提取Received→Revised时间的文件数: {len(valid_received_to_revised)}")
    print(f"成功提取Received→Accepted时间的文件数: {len(valid_received_to_accepted)}")
    if valid_received_to_revised:
        avg_received_to_revised = sum(valid_received_to_revised) / len(valid_received_to_revised)
        median_received_to_revised = median(valid_received_to_revised)
        min_received_to_revised = min(valid_received_to_revised)
        max_received_to_revised = max(valid_received_to_revised)
        print(f"\n【Received -> Revised 平均时间】: {avg_received_to_revised:.1f} 天 ({avg_received_to_revised/30:.1f} 个月)")
        print(f"   中位数: {median_received_to_revised:.1f} 天 ({median_received_to_revised/30:.1f} 个月)")
        print(f"   最短: {min_received_to_revised} 天 ({min_received_to_revised/30:.1f} 个月)")
        print(f"   最长: {max_received_to_revised} 天 ({max_received_to_revised/30:.1f} 个月)")
    else:
        print("\n[警告] 没有找到有效的Received->Revised时间数据")
    
    if valid_received_to_accepted:
        avg_received_to_accepted = sum(valid_received_to_accepted) / len(valid_received_to_accepted)
        median_received_to_accepted = median(valid_received_to_accepted)
        min_received_to_accepted = min(valid_received_to_accepted)
        max_received_to_accepted = max(valid_received_to_accepted)
        print(f"\n【Received -> Accepted 平均时间】: {avg_received_to_accepted:.1f} 天 ({avg_received_to_accepted/30:.1f} 个月)")
        print(f"   中位数: {median_received_to_accepted:.1f} 天 ({median_received_to_accepted/30:.1f} 个月)")
        print(f"   最短: {min_received_to_accepted} 天 ({min_received_to_accepted/30:.1f} 个月)")
        print(f"   最长: {max_received_to_accepted} 天 ({max_received_to_accepted/30:.1f} 个月)")
    else:
        print("\n[警告] 没有找到有效的Received->Accepted时间数据")
    
    print("\n" + "=" * 80)

def main():
    """主函数"""
    # PDF文件夹路径
    journal_name = "IEEE Sens J"
    pdf_folder = rf"journal article archive/{journal_name}"
    
    if not os.path.exists(pdf_folder):
        print(f"错误: 文件夹 '{pdf_folder}' 不存在")
        return
    
    # 处理所有PDF文件
    results = process_pdf_folder(pdf_folder)
    
    # 计算并显示统计结果
    if results:
        calculate_statistics(results, journal_name)
    else:
        print("\n⚠️  没有成功处理任何PDF文件")

if __name__ == "__main__":
    main()


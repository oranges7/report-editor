import os
import sys
import shutil
import chardet
import re
import openpyxl
import pandas as pd
import numpy as np
import argparse
import txttoword
from collections import OrderedDict
def print_usage():
    print("Usage: python Path/html_auto_report_nologo.py Report.txt", file=sys.stderr)
    print("""
Report.txt Format:
#Custom:名字
#Contract:项目编号
#Title:题目
#section:英文题目:(中文)#
#subsection# -- 用于副标题
#table:表名:表文件名# -- 用于表格
#graph:S1,S2,..:file1,file2,..# -- 用于图片
#link:S1,S2,..:file1,file2,..# -- 用于链接文件，但不做图或表展示
""", file=sys.stderr)
    sys.exit(0)


def clean_table_data(df):
    # Function to clean column names
    def clean_column_name(name):
        # Remove 'Unnamed: ' prefix and any following number
        cleaned_name = re.sub(r'^Unnamed: \d+', '', str(name))
        # If the name becomes empty after cleaning, replace with a space
        return ' ' if cleaned_name == '' else cleaned_name

    # Clean column names
    df.columns = [clean_column_name(col) for col in df.columns]

    # Remove columns where all values are NaN
    df = df.dropna(axis=1, how='all')

    # Replace NaN values with an empty string
    df = df.replace({np.nan: ''})

    return df

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # 读取前 10000 字节进行检测
        return result['encoding']


def read_table_file(file_path):
    encoding = detect_encoding(file_path)
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path, encoding=encoding)
    else:  # For .txt and other files
        df = pd.read_csv(file_path, sep='\t', encoding=encoding)

    return clean_table_data(df)


def generate_html_table(df, max_rows=100, max_width='100%', max_height='60vh'):
    """
    生成带独立滚动条的响应式表格
    Parameters:
        df (pd.DataFrame): 输入数据框
        max_rows (int): 最大显示行数
        max_width (str): 表格最大宽度 (CSS单位)
        max_height (str): 表格可视区域最大高度 (CSS单位)
    Returns:
        str: 完整 HTML 字符串
    """
    display_df = df.head(max_rows)
    has_scroll = len(df) > max_rows

    # 生成基础表格
    table_html = display_df.to_html(
        classes='table table-sm table-hover table-striped',
        index=False,
        na_rep='<span class="text-muted">N/A</span>',
        escape=False
    )

    # 添加滚动控制容器
    html_template = f"""
<div class="table-scroll-container" 
     style="max-width: {max_width}; max-height: {max_height};">
    <style>
        .table-scroll-container {{
            overflow: auto;
            border: 1px solid #dee2e6;
            border-radius: 0.375rem;
            box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
            position: relative;
        }}

        /* 固定表头 */
        .table-scroll-container table thead th {{
            position: sticky !important; /* 保留 !important 确保覆盖 */
            top: 0 !important;
            background: #2e6da4 !important;
            z-index: 2;
            box-shadow: 0 2px 2px -1px rgba(0,0,0,0.1);
        }}

        /* 列宽自适应 */
        .table-scroll-container table {{
            min-width: 600px;
            table-layout: auto;
            margin-bottom: 0;
        }}

        /* 优化单元格展示 */
        .table-scroll-container td {{
            max-width: 400px;
            white-space: normal;
            word-wrap: break-word; 
            vertical-align: middle;
        }}

        /* 滚动条样式 */
        .table-scroll-container::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        .table-scroll-container::-webkit-scrollbar-thumb {{
            background: #ced4da;
            border-radius: 4px;
        }}
    </style>

    {table_html}
</div>

{'' if not has_scroll else f'''
<div class="mt-2 text-end small text-muted">
    显示前 {max_rows} 行 (共 {len(df)} 行)
</div>'''}
    """

    return html_template



additional_css = """
<style>
    .table-responsive {
        max-height: 500px;
        overflow-y: auto;
    }
    .table-responsive thead th {
        position: sticky;
        top: 0;
        background-color: #2e6da4;
        z-index: 1;
    }
    .nav li.active a {
        background-color: #e7e7e7;
        color: #555;
        font-weight: bold;
    }
</style>
"""
def write_html_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


image_count = 1
table_count = 1


def generate_html_content(info, section_text, main_text, additional_css=""):
    global image_count, table_count

    # 配置参数


    # 初始化 HTML 结构
    html_content = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="zh_CN" xmlns="http://www.w3.org/1999/xhtml"><head><title>{info['Title']}</title>
<meta charset="UTF-8"></meta>
<!--[if lt IE 9]>
<script src="src/js/html5shiv.min.js"></script><script src="src/js/respond.min.js"></script>
<![endif]-->
<meta author="huangls@biomarker.com.cn, designed by zhengj@biomarker.com.cn"></meta>
<meta content="IE=edge" http-equiv="X-UA-Compatible"></meta>
<meta content="width=device-width, initial-scale=1" name="viewport"></meta>
<link href="src/css/bootstrap.min.css" type="text/css" rel="stylesheet" />
<link href="src/css/index.css" type="text/css" rel="stylesheet" />
<link href="src/js/fancyBox/jquery.fancybox.css" type="text/css" rel="stylesheet" />
<link href="src/css/nav.css" type="text/css" rel="stylesheet" />
<link href="src/css/raxus.css" type="text/css" rel="stylesheet" />
<script src="src/js/jquery-1.11.3.min.js" type="text/javascript"></script>
<script src="src/js/nav.js" type="text/javascript"></script>
<script src="src/js/raxus-slider.min.js" type="text/javascript"></script>
<script src="src/js/fancyBox/jquery.fancybox.pack.js" type="text/javascript"></script>
<script src="src/js/fancyBox/jquery.mousewheel-3.0.6.pack.js" type="text/javascript"></script>
<script src="src/js/bootstrap.min.js" type="text/javascript"></script>
<script src="src/js/ready.js" type="text/javascript"></script>
<script src="src/js/scrolltop.js" type="text/javascript"></script>
<script src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>
<script src="src/js/mathjax.js" type="text/javascript"></script>
</head>
<body><title>{info['Title']}</title>

<div class="container shadow">
    <header><img src="src/images/logo.png" class="pull-right" /></header>
<div class="row">
    <div role="main" class="col-md-9">
        <header><h2 id="title" class="text-center">{info['Title']}</h2></header>"""


    # 主内容生成
    navigator = f"""
    <div role="complementary" class="col-md-3"><nav class="bs-docs-sidebar hidden-print hidden-xs hidden-sm affix-top"><ul class="nav bs-docs-sidenav"><li><a href="#a9">目录</a>
</li>"""
    s_id = 0
    b_nav = 0
    for section_id, content in section_text.items():
        s_id += 1
        section_num="a"+str(s_id)
        html_content += f"""
        <section><h3 id="{section_num}">{content['chinese_title']}</h3>"""
        navigator += f"""
        <li><a href="#{section_num}">{str(s_id)} {content['chinese_title']}</a>"""
        sub = 0
        sub_sub = 0  # h5计数器
        sub_sub_sub = 0  # h6计数器
        for line in content["main_text"]:
            if '#subsection#' in line:
                sub += 1
                b_nav += 1
                sub_id = "b"+str(b_nav)
                sub_num = str(s_id)+"."+str(sub)
                text = line.split('#subsection')[0].strip()
                html_content += f"""
                    <h4 class="title-h4" id="{sub_id}">{sub_num} {text}</h4>"""
                navigator += f"""
                    <ul class="nav"><li><a href="#{sub_id}" class="js-active-bg">{sub_num} {text}</a></ul>"""
            elif '#h5' in line:  # 添加h5标记识别
                sub_sub += 1
                sub_sub_sub = 0  # 重置h6计数器
                text = line.split('#h5#')[0].strip()
                h5_id = f"c0{sub_sub}"
                h5_num = f"{s_id}.{sub}.{sub_sub}"  # 计算完整编号
                html_content += f"""
                            <h5 id="{h5_id}" class="title-h5">{h5_num} {text}</h5>"""  # 添加带编号的h5

            elif '#h6' in line:  # 添加h6标记识别
                sub_sub_sub += 1
                text = line.split('#h6#')[0].strip()
                h6_id = f"d0{sub_sub_sub}"
                h6_num = f"{s_id}.{sub}.{sub_sub}.{sub_sub_sub}"  # 计算完整编号
                html_content += f"""
                            <h5 id="{h6_id}" class="title-h5">{text}</h5>"""  # 添加带编号的h5
            elif '#graph' in line:
                parts = line.split(':')
                title = parts[1].strip()
                file = parts[2].split('#')[0].strip()
                pdf_file = file.rsplit('.', 1)[0] + '.pdf'
                if os.path.exists(pdf_file):
                    html_content += f"""
                    <p class="text-center">
                        <a title="图{image_count} {title}" href="{file}" class="img-toggle"><img src="{file}" alt="{file}" class="img-width-normal" /></a>
                    </p><p class="img-mark text-center">图{image_count} {title}</b>(<a href="{pdf_file}" target="_blank">下载</a>)</p>
                    """
                else:
                    html_content += f"""
                    <p class="text-center">
                        <a title="图{image_count} {title}" href="{file}" class="img-toggle"><img src="{file}" alt="{file}" class="img-width-normal" /></a>
                    </p><p class="img-mark text-center">图{image_count} {title}</b>(<a href="{file}" target="_blank">下载</a>)</p>
                    """
                image_count += 1
            elif '#span' in line:
                parts = line.split(':')
                title = parts[1].strip()
                html_content += f"""
                    <p class="img-mark text-center">{title}</p>
                    """
            elif '#paper' in line:
                parts = line.split('#')
                paper = parts[2].strip()
                html_content += f"""<div class="paper">
                    <div >{paper}</div>
                    </div>
                    """

            elif '#table' in line:
                parts = line.split(':')
                title = parts[1].strip()
                file = parts[2].split('#')[0].strip()

                html_content += f"""
                    <div class="card border-light shadow-sm mt-4">
                        <div class="card-header bg-light d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center">
                                <p class="img-mark text-center">表 {table_count} {title}</b>(<a href="{file}" target="_blank">下载</a>)</p>    
                            </div>    
                        </div>
                        <div class="card-body">"""

                try:
                    df = read_table_file(file)
                    html_content += generate_html_table(df)
                except Exception as e:
                    html_content += f"""
                            <div class="alert alert-danger">
                                <i class="bi bi-exclamation-triangle me-2"></i>
                                表格加载错误: {str(e)}
                            </div>"""

                html_content += """
                        </div>
                    </div>"""
                table_count += 1
            elif '#ann' in line:
                parts = line.split(':')
                ann = parts[2].strip()
                html_content += f"""
                < p class ="paragraph" style="font-size:12px;color:#D8BFD8" > {ann} < / p >"""
            elif '#link' in line:
                parts = line.split(':')
                title = parts[1].strip()
                file = parts[2].split('#')[0].strip()
                html_content += f"""
                <p class="img-mark text-center"><a href="{file}">{title}</a></p>"""
            elif line.strip():
                html_content += f"""
                    <p class="paragraph">{line}</p>"""

        html_content += """
        </section>"""
        navigator += f"""
                </li>"""
    html_content += f""" 
</div>"""

    navigator +=f"""
    </ul>
</nav>
</div>
</div>"""

    footer_content = f"""
<footer><div class="text-center"><p>Copyright © 2025 微宇山东生物科技有限公司版权所有</p>
<p>公司地址：山东省济南市高新区药谷研发平台2号楼18层</p>
<li>E-mail:<a href="mailto:omniomics@126.com">omniomics@126.com;</a></li>
</ul>
</div>
</footer>
<div id="goTop"><a title="Top" class="backtotop"><img src="src/images/gotop.png" class="back-tip" />
</a>
</div>
</div>
</body>
</html>
    """
    html_content += navigator
    html_content += footer_content
    return html_content

# 定义一个通用函数来处理运行时路径
def resource_path(relative_path):
    """获取资源的绝对路径（支持 PyInstaller 打包后）"""
    if hasattr(sys, '_MEIPASS'):
        # 如果是 PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 如果是普通运行（未打包时）
    return os.path.join(os.path.abspath("."), relative_path)

# 修改你的路径检查和拷贝逻辑
source_path = resource_path('src')  # 替换硬编码路径
destination_path = './src'




def get_unique_dirname(base_name):
    """自动生成带编号的唯一目录名"""
    counter = 0
    while True:
        dir_name = f"{base_name}{counter if counter else ''}"
        if not os.path.exists(dir_name):
            return dir_name
        counter += 1

def main(input_file, generate_word=True):
    # 确保资源目录存在
    resource_dirs = ['src']
    for res_dir in resource_dirs:
        if not os.path.exists(res_dir):

            shutil.copytree(source_path, destination_path)

    global image_count, table_count
    image_count = 1
    table_count = 1
    info = {}
    section_text = OrderedDict()  # 使用有序字典保持章节顺序
    current_section = None

    # 解析输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('##'):
                # 处理元信息
                type_, content = line.split(':', 1)
                info[type_.strip('#')] = content
            elif '#section:' in line:
                # 新建章节
                section_info = line.split('#section:')[1].split('#')[0]
                chinese, english = section_info.split(':', 1)
                section_id = f"section{len(section_text)+1}"
                section_text[section_id] = {
                    "chinese_title": chinese.strip(),
                    "english_title": english.strip(),
                    "main_text": []
                }
                current_section = section_id
            elif current_section:
                # 添加章节内容
                section_text[current_section]["main_text"].append(line)

    # 生成唯一报告目录
    report_name = f"{info.get('Contract', '未命名')}分析报告"
    dir_name = get_unique_dirname(report_name)
    os.makedirs(dir_name, exist_ok=True)
    if os.path.exists('result'):
        shutil.copytree('result', f"{dir_name}/result")
    # 生成完整HTML内容
    html_content = generate_html_content(
        info=info,
        section_text=section_text,
        main_text=[]
    )

    # 写入主文件
    main_html_path = os.path.join(dir_name, f"{report_name}.html")
    with open(main_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 复制依赖资源
    for res_dir in resource_dirs:
        src = os.path.abspath(res_dir)
        dst = os.path.join(dir_name, res_dir)
        if os.path.exists(src) and not os.path.exists(dst):
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

    # 生成辅助文件
    readme_path = os.path.join(dir_name, "使用说明.txt")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"""报告导航说明：
1. 主文件：{report_name}.html
2. 使用浏览器打开后可通过右侧导航菜单快速定位
3. 所有图表均支持点击下载高清版本
4. 按Ctrl+F可在当前章节内搜索内容""")

    # 生成Word文档
    if generate_word:
        txttoword.create_formatted_word(input_file, dir_name)

    print(f"报告生成成功！保存路径：{os.path.abspath(dir_name)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file.")
    parser.add_argument("-w", "--work_dir",type=str,default=None,help="工作目录（默认为当前目录）")
    parser.add_argument("-r", "--report", type=str, default="Report.txt",
                        help="报告文件（默认：Report.txt）")
    parser.add_argument("-m", "--word", action="store_true",
                        help="生成 Word 文档（默认不生成）")
    # 解析参数
    args = parser.parse_args()
    if args.work_dir:
        os.chdir(args.work_dir)
        print(f"工作目录已切换至：{os.getcwd()}")
    if not os.path.exists(args.report):
        print("Error: 报告文本文件不存在.")
        print_usage()
        sys.exit(1)
    report_file = args.report
    generate_word = args.word  # 如果传了 --no-word，则不生成
    main(report_file, generate_word)

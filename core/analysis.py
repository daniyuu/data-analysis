import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
import datetime
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from core.xingyun_service import XingyunService

client = XingyunService(api_key=os.getenv("XINGYUN_API_KEY"))


def read_data_file(file_path):
    """智能读取Excel文件，优化多级表头处理"""
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension not in [".xlsx", ".xls"]:
        raise ValueError(f"不支持的文件格式: {file_extension}")

    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, engine="openpyxl")

        # 检查是否有多级表头
        if isinstance(df.columns, pd.MultiIndex):
            # 处理多级表头，合并为单级
            new_columns = []
            for col in df.columns:
                if isinstance(col, tuple):
                    # 合并多级表头，去除空值和重复值
                    col_parts = []
                    for part in col:
                        if pd.notna(part) and str(part).strip():
                            col_parts.append(str(part).strip())

                    if col_parts:
                        # 去除重复的部分
                        unique_parts = []
                        for part in col_parts:
                            if part not in unique_parts:
                                unique_parts.append(part)
                        new_col = "_".join(unique_parts)
                    else:
                        new_col = f"列{len(new_columns)+1}"
                else:
                    new_col = str(col)
                new_columns.append(new_col)

            df.columns = new_columns
            print(f"成功处理多级表头，合并后的列名: {list(df.columns)}")

        return df

    except Exception as e:
        raise Exception(f"读取文件失败: {str(e)}")


def clean_dataframe(df):
    """清理数据框，处理常见的数据问题"""
    # 复制数据框避免修改原始数据
    df_clean = df.copy()

    # 1. 清理列名
    df_clean.columns = [str(col).strip() for col in df_clean.columns]

    # 2. 移除完全为空的行和列
    df_clean = df_clean.dropna(how="all")
    df_clean = df_clean.dropna(axis=1, how="all")

    # 3. 处理数值型列中的非数值数据
    for col in df_clean.select_dtypes(include=["object"]).columns:
        try:
            # 移除常见的非数值字符
            temp_series = df_clean[col].astype(str)
            temp_series = temp_series.str.replace(",", "").str.replace("，", "")
            temp_series = (
                temp_series.str.replace("$", "")
                .str.replace("¥", "")
                .str.replace("￥", "")
            )
            temp_series = temp_series.str.replace(" ", "").str.replace("　", "")
            temp_series = temp_series.str.replace("(", "").str.replace(")", "")
            temp_series = temp_series.str.replace("（", "").str.replace("）", "")

            # 尝试转换为数值
            pd.to_numeric(temp_series, errors="raise")
            df_clean[col] = pd.to_numeric(temp_series, errors="coerce")
            print(f"列 '{col}' 已转换为数值型")
        except:
            # 如果转换失败，保持原样
            pass

    # 4. 处理日期列
    for col in df_clean.columns:
        if any(
            keyword in str(col).lower()
            for keyword in ["date", "time", "日期", "时间", "年", "月", "日"]
        ):
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")
                print(f"列 '{col}' 已转换为日期型")
            except:
                pass

    return df_clean


async def generate_html_from_excel(excel_path):
    """
    从Excel文件生成HTML分析报告

    Args:
        excel_path (str): Excel文件路径

    Returns:
        str: 生成的HTML文件路径
    """
    try:
        # 读取Excel文件
        df = read_data_file(excel_path)
        df = clean_dataframe(df)

        # 将数据转换为CSV格式的字符串，方便发送给大模型
        csv_data = df.to_csv(index=False, encoding="utf-8")

        # 构建分析prompt
        analysis_prompt = f"""##任务
你是一个面向公司资金财务人员的智能数据分析助手。当用户上传任意Excel表格后，请：
1. 智能分析表格中的数据内容，识别主要的变量、指标和数据维度。
2. 自动推荐2-4种最适合用来可视化本次数据的图表类型（如柱状图、折线图、饼图、散点图等），并简要说明推荐理由。
3. 使用HTML和CSS代码生成数据可视化图表，确保图表直观清晰，能为财务管理与决策提供有效支持。如遇表头不清或数据有歧义，请合理假设并在结果中注明。

##要求
最后输出应包含：
1. 数据主要内容和发现的简要总结
2. 图表类型推荐及理由说明
3. 使用HTML+CSS+JavaScript生成的可视化图表（不要使用图片，要用代码绘制）

##输出格式
所有的输出全部使用一个html网页输出，图表必须用HTML/CSS/JavaScript代码实现，不要生成图片文件。

##图表要求
- 使用HTML表格、CSS样式和JavaScript来创建图表
- 可以使用Chart.js、D3.js或其他JavaScript图表库
- 图表要响应式，适配不同屏幕尺寸
- 颜色搭配要专业美观
- 数据标签要清晰可读

##数据内容
以下是Excel文件的数据内容（CSV格式）：
{csv_data}

请根据以上数据进行分析并生成HTML报告，确保所有图表都是用代码实现的，不要使用图片。"""

        # 发送给大模型进行分析

        response = client.chat_with_text(
            text=analysis_prompt,
            chat_id="test_chat_001",
        )

        # 获取大模型的HTML输出
        # 星云API的响应格式与OpenAI不同
        if "choices" in response and len(response["choices"]) > 0:
            html_content = response["choices"][0]["message"]["content"]
        elif "message" in response:
            html_content = response["message"]["content"]
        elif "content" in response:
            html_content = response["content"]
        else:
            # 如果响应格式不明确，尝试直接获取内容
            html_content = str(response)

        # 保存HTML报告
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "reports",
            f"ai_analysis_report_{now}.html",
        )
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return report_path

    except Exception as e:
        raise Exception(f"生成HTML报告失败: {str(e)}")


def analyze_excel_sync(excel_path):
    """
    同步版本的Excel分析函数（用于非异步环境）

    Args:
        excel_path (str): Excel文件路径

    Returns:
        tuple: (success, result_or_error_message)
    """
    import asyncio

    try:
        # 在事件循环中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate_html_from_excel(excel_path))
        loop.close()
        return True, result
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    analyze_excel_sync("examples/授信数据mock.xlsx")

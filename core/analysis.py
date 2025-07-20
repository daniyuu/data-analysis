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
from config import REPORT_DIR
from core.prompt import DEFAULT_ANALYSIS_PROMPT

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


async def generate_html_from_excel(
    excel_path, chat_id, analysis_prompt=None, user_content=None
):
    """
    从Excel文件生成HTML分析报告

    Args:
        excel_path (str): Excel文件路径
        uid (str): 用户ID，用作chat_id

    Returns:
        str: 生成的HTML文件路径
    """
    try:
        # 读取Excel文件
        df = read_data_file(excel_path)
        df = clean_dataframe(df)

        # 将数据转换为CSV格式的字符串，方便发送给大模型
        csv_data = df.to_csv(index=False, encoding="utf-8")

        analysis_prompt = (
            analysis_prompt if analysis_prompt else DEFAULT_ANALYSIS_PROMPT
        )

        # 构建分析prompt

        if user_content:
            prompt = f"""{analysis_prompt}
## 示例数据
以下是Excel文件的数据内容（CSV格式）：
{csv_data}
请根据以上数据以及用户问题进行分析并生成HTML报告，确保所有图表都是用代码实现的，不要使用图片。

## 用户问题
{user_content}
"""
        else:
            prompt = f"""{analysis_prompt}
## 示例数据
以下是Excel文件的数据内容（CSV格式）：
{csv_data}
请根据以上数据进行分析并生成HTML报告，确保所有图表都是用代码实现的，不要使用图片。"""

        response = client.chat_with_text(
            text=prompt,
            chat_id=chat_id,
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
        report_path = os.path.join(REPORT_DIR, f"ai_analysis_report_{now}.html")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return report_path

    except Exception as e:
        raise Exception(f"生成HTML报告失败: {str(e)}")


def analyze_excel_sync(excel_path, uid=None):
    """
    同步版本的Excel分析函数（用于非异步环境）

    Args:
        excel_path (str): Excel文件路径
        uid (str): 用户ID，用作chat_id

    Returns:
        tuple: (success, result_or_error_message)
    """
    import asyncio

    try:
        # 在事件循环中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate_html_from_excel(excel_path, uid))
        loop.close()
        return True, result
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    analyze_excel_sync("examples/授信数据mock.xlsx")

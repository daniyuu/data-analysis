import chainlit as cl
import pandas as pd
from config import gpt_client, AZURE_DEPLOYMENT_NAME
import os

import matplotlib.pyplot as plt
import matplotlib
import openpyxl


# 设置中文字体
def setup_chinese_font():
    """设置中文字体，使用项目中的字体文件"""
    import matplotlib.font_manager as fm
    import os

    # 字体文件路径
    font_path = os.path.join(os.path.dirname(__file__), "resource", "simhei.ttf")

    if os.path.exists(font_path):
        # 添加字体文件到matplotlib字体管理器
        font_prop = fm.FontProperties(fname=font_path)

        # 设置全局字体
        matplotlib.rcParams["font.family"] = "sans-serif"
        matplotlib.rcParams["font.sans-serif"] = [
            font_prop.get_name(),
            "SimHei",
            "DejaVu Sans",
        ]

        print(f"成功加载中文字体: {font_path}")
    else:
        print(f"警告: 字体文件不存在: {font_path}")
        # 尝试使用系统字体作为备选
        try:
            matplotlib.rcParams["font.family"] = "SimHei"
            print("使用系统SimHei字体")
        except:
            print("警告: 无法找到合适的中文字体，将使用英文显示")
            matplotlib.rcParams["font.family"] = "sans-serif"

    matplotlib.rcParams["axes.unicode_minus"] = False  # 正常显示负号


# 初始化中文字体
setup_chinese_font()
import seaborn as sns
import uuid
import base64
import datetime
import numpy as np

client = gpt_client

# Instrument the OpenAI client
cl.instrument_openai()


# 设置现代化的图表样式
def setup_modern_style():
    """设置现代化的图表样式"""
    # 设置seaborn样式
    sns.set_style("whitegrid")
    sns.set_palette("husl")

    # 设置matplotlib参数
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "#f8f9fa"
    plt.rcParams["axes.edgecolor"] = "#dee2e6"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#e9ecef"
    plt.rcParams["grid.linestyle"] = "-"
    plt.rcParams["grid.linewidth"] = 0.5
    plt.rcParams["grid.alpha"] = 0.7
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["figure.titlesize"] = 16

    # 重新应用中文字体设置（seaborn可能会覆盖字体设置）
    import matplotlib.font_manager as fm
    import os

    font_path = os.path.join(os.path.dirname(__file__), "resource", "simhei.ttf")
    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [
            font_prop.get_name(),
            "SimHei",
            "DejaVu Sans",
        ]


def create_gradient_colors(n_colors):
    """创建渐变色彩"""
    if n_colors <= 0:
        return ["#3498db"]  # 返回默认颜色
    colors = plt.cm.viridis(np.linspace(0, 1, n_colors))
    return colors


def add_modern_effects(ax, title, xlabel=None, ylabel=None):
    """为图表添加现代化效果"""
    # 设置标题样式
    ax.set_title(title, fontsize=14, fontweight="bold", pad=20, color="#2c3e50")

    # 设置轴标签
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12, color="#34495e", fontweight="500")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12, color="#34495e", fontweight="500")

    # 美化坐标轴
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#bdc3c7")
    ax.spines["bottom"].set_color("#bdc3c7")

    # 设置网格
    ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

    # 设置背景色
    ax.set_facecolor("#f8f9fa")


def create_modern_bar_chart(data, title, figsize=(10, 6)):
    """创建现代化的柱状图"""
    fig, ax = plt.subplots(figsize=figsize)

    # 确保数据不为空
    if len(data) == 0:
        return fig, ax

    # 创建渐变色彩
    colors = create_gradient_colors(len(data))

    # 安全地获取数据值
    try:
        if hasattr(data, "values"):
            data_values = list(data.values())
        else:
            data_values = list(data)
    except Exception:
        data_values = list(data)

    try:
        if hasattr(data, "keys"):
            data_keys = list(data.keys())
        else:
            data_keys = [str(i) for i in range(len(data_values))]
    except Exception:
        data_keys = [str(i) for i in range(len(data_values))]

    bars = ax.bar(
        range(len(data_values)),
        data_values,
        color=colors,
        edgecolor="white",
        linewidth=1,
        alpha=0.8,
    )

    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, data_values)):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01 * max(data_values),
            f"{value}",
            ha="center",
            va="bottom",
            fontweight="bold",
            color="#2c3e50",
        )

    # 设置x轴标签
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data_keys, rotation=45, ha="right")

    add_modern_effects(ax, title, "类别", "计数")

    return fig, ax


def create_modern_histogram(data, title, num_bins=20, figsize=(10, 6)):
    """创建现代化的直方图"""
    fig, ax = plt.subplots(figsize=figsize)

    # 创建渐变色彩
    colors = plt.cm.viridis(0.6)

    # 绘制直方图
    n, bins, patches = ax.hist(
        data, bins=num_bins, color=colors, alpha=0.7, edgecolor="white", linewidth=1
    )

    # 添加密度曲线
    from scipy import stats

    kde_x = np.linspace(data.min(), data.max(), 100)
    kde = stats.gaussian_kde(data)
    kde_y = kde(kde_x) * len(data) * (bins[1] - bins[0])
    ax.plot(kde_x, kde_y, color="#e74c3c", linewidth=2, alpha=0.8)

    add_modern_effects(ax, title, "数值", "频数")

    return fig, ax


def create_modern_scatter(x, y, title, figsize=(10, 6)):
    """创建现代化的散点图"""
    fig, ax = plt.subplots(figsize=figsize)

    # 创建渐变色彩
    x_len = len(x) if hasattr(x, "__len__") else 100
    colors = plt.cm.plasma(np.linspace(0, 1, x_len))

    # 绘制散点图
    scatter = ax.scatter(
        x, y, c=colors, alpha=0.6, s=50, edgecolors="white", linewidth=0.5
    )

    # 添加趋势线
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(x, p(x), "r--", alpha=0.8, linewidth=2)

    # 安全地获取列名
    x_name = getattr(x, "name", "X轴")
    y_name = getattr(y, "name", "Y轴")
    add_modern_effects(ax, title, x_name, y_name)

    return fig, ax


def create_modern_line_chart(x, y_dict, title, figsize=(12, 6)):
    """创建现代化的折线图"""
    fig, ax = plt.subplots(figsize=figsize)

    # 创建渐变色彩
    colors = create_gradient_colors(len(y_dict))

    for (name, y), color in zip(y_dict.items(), colors):
        ax.plot(
            x,
            y,
            color=color,
            linewidth=2.5,
            alpha=0.8,
            label=name,
            marker="o",
            markersize=4,
        )

    add_modern_effects(ax, title, "时间", "数值")
    ax.legend(frameon=True, fancybox=True, shadow=True, loc="best")

    return fig, ax


def create_modern_boxplot(data, title, figsize=(8, 6)):
    """创建现代化的箱线图"""
    fig, ax = plt.subplots(figsize=figsize)

    # 创建渐变色彩
    colors = plt.cm.Set3(0.6)

    # 绘制箱线图
    bp = ax.boxplot(
        data,
        patch_artist=True,
        boxprops=dict(facecolor=colors, alpha=0.7, edgecolor="#2c3e50"),
        medianprops=dict(color="#e74c3c", linewidth=2),
        flierprops=dict(marker="o", markerfacecolor="#3498db", markersize=4),
    )

    add_modern_effects(ax, title, "", "数值")
    # 安全地获取数据名称
    data_name = getattr(data, "name", "数据")
    ax.set_xticklabels([data_name])

    return fig, ax


def create_modern_heatmap(corr_matrix, title, figsize=(10, 8)):
    """创建现代化的热力图"""
    fig, ax = plt.subplots(figsize=figsize)

    # 创建掩码矩阵（隐藏对角线）
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    # 绘制热力图
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
        fmt=".2f",
        annot_kws={"size": 10},
    )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20, color="#2c3e50")

    return fig, ax


def create_modern_pie_chart(data, title, figsize=(8, 8)):
    """创建现代化的饼图"""
    fig, ax = plt.subplots(figsize=figsize)

    # 确保数据不为空
    if len(data) == 0:
        return fig, ax

    # 创建渐变色彩
    colors = create_gradient_colors(len(data))

    # 安全地获取数据值
    try:
        if hasattr(data, "values"):
            data_values = list(data.values())
        else:
            data_values = list(data)
    except Exception:
        data_values = list(data)

    try:
        if hasattr(data, "keys"):
            data_keys = list(data.keys())
        else:
            data_keys = [str(i) for i in range(len(data_values))]
    except Exception:
        data_keys = [str(i) for i in range(len(data_values))]

    # 确保数据不为空
    if len(data_values) == 0:
        return fig, ax

    wedges, texts, autotexts = ax.pie(
        data_values,
        labels=data_keys,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.7, edgecolor="white", linewidth=2),
    )

    # 美化文本
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20, color="#2c3e50")

    return fig, ax


# 初始化现代化样式
setup_modern_style()


def read_data_file(file_path):
    """智能读取CSV或Excel文件"""
    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        if file_extension == ".csv":
            # 尝试不同的编码方式读取CSV
            encodings = ["utf-8", "gbk", "gb2312", "utf-8-sig"]
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    return df
                except UnicodeDecodeError:
                    continue
            # 如果所有编码都失败，使用默认编码
            return pd.read_csv(file_path)

        elif file_extension in [".xlsx", ".xls"]:
            # 读取Excel文件
            return pd.read_excel(file_path, engine="openpyxl")

        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")

    except Exception as e:
        raise Exception(f"读取文件失败: {str(e)}")


# 自动生成图表并保存为图片，返回图片路径列表
@cl.step(type="tool")
def generate_charts(file_path, output_dir="charts"):
    df = read_data_file(file_path)
    img_paths = []
    os.makedirs(output_dir, exist_ok=True)

    # 1. 现代化的柱状图/条形图：分类变量的计数
    for col in df.select_dtypes(include=["object", "category"]):
        if df[col].nunique() < 20:
            try:
                data = df[col].value_counts()
                # 确保数据不为空
                if len(data) == 0:
                    print(f"跳过空数据列: {col}")
                    continue

                # 转换为字典以确保兼容性
                data_dict = data.to_dict()
                fig, ax = create_modern_bar_chart(data_dict, f"{col} 分布分析")
                plt.tight_layout()
                img_path = os.path.join(
                    output_dir, f"{col}_bar_{uuid.uuid4().hex[:8]}.png"
                )
                plt.savefig(img_path, dpi=300, bbox_inches="tight", facecolor="white")
                plt.close()
                img_paths.append(img_path)
            except Exception as e:
                print(f"生成柱状图时出错 {col}: {str(e)}")
                continue

    # 2. 现代化的数值型变量直方图
    for col in df.select_dtypes(include=["number"]):
        data = df[col].dropna()
        if len(data) > 0:
            try:
                fig, ax = create_modern_histogram(data, f"{col} 分布分析")
                plt.tight_layout()
                img_path = os.path.join(
                    output_dir, f"{col}_hist_{uuid.uuid4().hex[:8]}.png"
                )
                plt.savefig(img_path, dpi=300, bbox_inches="tight", facecolor="white")
                plt.close()
                img_paths.append(img_path)
            except Exception as e:
                print(f"生成直方图时出错 {col}: {str(e)}")
                continue

    # 3. 现代化的数值型变量散点图（只画前两个数值型变量）
    num_cols = df.select_dtypes(include=["number"]).columns
    if len(num_cols) >= 2:
        try:
            x_data = df[num_cols[0]].dropna()
            y_data = df[num_cols[1]].dropna()
            # 确保x和y长度一致
            min_len = min(len(x_data), len(y_data))
            x_data = x_data.iloc[:min_len]
            y_data = y_data.iloc[:min_len]

            fig, ax = create_modern_scatter(
                x_data, y_data, f"{num_cols[0]} vs {num_cols[1]} 关系分析"
            )
            plt.tight_layout()
            img_path = os.path.join(output_dir, f"scatter_{uuid.uuid4().hex[:8]}.png")
            plt.savefig(img_path, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()
            img_paths.append(img_path)
        except Exception as e:
            print(f"生成散点图时出错: {str(e)}")
            # 继续处理其他图表

    # 4. 现代化的时间序列折线图
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
                y_dict = {}
                for num_col in num_cols:
                    y_dict[num_col] = df[num_col].dropna()

                if len(y_dict) > 0:
                    fig, ax = create_modern_line_chart(
                        df[col], y_dict, f"{col} 时间序列分析"
                    )
                    plt.tight_layout()
                    img_path = os.path.join(
                        output_dir, f"{col}_line_{uuid.uuid4().hex[:8]}.png"
                    )
                    plt.savefig(
                        img_path, dpi=300, bbox_inches="tight", facecolor="white"
                    )
                    plt.close()
                    img_paths.append(img_path)
            except Exception:
                continue

    # 5. 现代化的箱线图
    for col in df.select_dtypes(include=["number"]):
        data = df[col].dropna()
        if len(data) > 0:
            try:
                fig, ax = create_modern_boxplot(data, f"{col} 箱线图分析")
                plt.tight_layout()
                img_path = os.path.join(
                    output_dir, f"{col}_box_{uuid.uuid4().hex[:8]}.png"
                )
                plt.savefig(img_path, dpi=300, bbox_inches="tight", facecolor="white")
                plt.close()
                img_paths.append(img_path)
            except Exception as e:
                print(f"生成箱线图时出错 {col}: {str(e)}")
                continue

    # 6. 现代化的热力图（相关性）
    if len(num_cols) >= 2:
        try:
            corr_matrix = df[num_cols].corr()
            fig, ax = create_modern_heatmap(corr_matrix, "数值型变量相关性热力图")
            plt.tight_layout()
            img_path = os.path.join(output_dir, f"heatmap_{uuid.uuid4().hex[:8]}.png")
            plt.savefig(img_path, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()
            img_paths.append(img_path)
        except Exception as e:
            print(f"生成热力图时出错: {str(e)}")
            # 继续处理其他图表

    # 7. 现代化的饼图
    for col in df.select_dtypes(include=["object", "category"]):
        if df[col].nunique() < 10:
            try:
                data = df[col].value_counts()
                # 确保数据不为空
                if len(data) == 0:
                    print(f"跳过空数据列: {col}")
                    continue

                # 转换为字典以确保兼容性
                data_dict = data.to_dict()
                fig, ax = create_modern_pie_chart(data_dict, f"{col} 占比分析")
                plt.tight_layout()
                img_path = os.path.join(
                    output_dir, f"{col}_pie_{uuid.uuid4().hex[:8]}.png"
                )
                plt.savefig(img_path, dpi=300, bbox_inches="tight", facecolor="white")
                plt.close()
                img_paths.append(img_path)
            except Exception as e:
                print(f"生成饼图时出错 {col}: {str(e)}")
                continue

    # 8. 现代化的成对关系图（Pairplot）
    if len(num_cols) >= 2:
        try:
            # 使用seaborn的pairplot但应用现代化样式
            pairplot = sns.pairplot(
                df[num_cols],
                diag_kind="kde",
                plot_kws={"alpha": 0.6, "s": 30},
                diag_kws={
                    "fill": True,
                    "alpha": 0.7,
                },  # 新版本seaborn使用fill而不是shade
            )

            # 设置标题字体
            import matplotlib.font_manager as fm

            font_path = os.path.join(
                os.path.dirname(__file__), "resource", "simhei.ttf"
            )
            font_prop = None
            if os.path.exists(font_path):
                font_prop = fm.FontProperties(fname=font_path)

            if font_prop:
                pairplot.fig.suptitle(
                    "数值型变量成对关系分析",
                    y=1.02,
                    fontsize=16,
                    fontweight="bold",
                    fontproperties=font_prop,
                )
            else:
                pairplot.fig.suptitle(
                    "数值型变量成对关系分析", y=1.02, fontsize=16, fontweight="bold"
                )
            pairplot.fig.patch.set_facecolor("white")

            # 美化每个子图
            for ax in pairplot.axes.flat:
                if ax is not None:
                    ax.set_facecolor("#f8f9fa")
                    ax.grid(True, alpha=0.3)
                    for spine in ax.spines.values():
                        spine.set_color("#bdc3c7")

            img_path = os.path.join(output_dir, f"pairplot_{uuid.uuid4().hex[:8]}.png")
            pairplot.savefig(img_path, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()
            img_paths.append(img_path)
        except Exception as e:
            print(f"生成成对关系图时出错: {str(e)}")
            # 继续处理其他图表

    return img_paths


def generate_html_report(
    all_img_paths, all_explanations, summary, output_path="analysis_report.html"
):
    # 图片转base64
    img_html = ""
    for img_path, explain in zip(all_img_paths, all_explanations):
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        img_html += f"""
        <div class="chart-block">
            <img src="data:image/png;base64,{img_b64}" class="chart-img"/>
            <div class="chart-explain">{explain}</div>
        </div>
        """
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>数据分析报告</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                line-height: 1.6;
                min-height: 100vh;
                padding: 20px 0;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                padding: 40px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 30px;
                border-bottom: 3px solid linear-gradient(90deg, #667eea, #764ba2);
                background: linear-gradient(90deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                font-weight: 700;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }}
            
            .header .subtitle {{
                font-size: 1.1em;
                color: #666;
                font-weight: 300;
            }}
            
            .summary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                margin-bottom: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
                position: relative;
                overflow: hidden;
            }}
            
            .summary::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
                pointer-events: none;
            }}
            
            .summary strong {{
                font-size: 1.2em;
                display: block;
                margin-bottom: 15px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            }}
            
            .chart-block {{
                margin-bottom: 40px;
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.2);
                position: relative;
                overflow: hidden;
            }}
            
            .chart-block:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
            }}
            
            .chart-block::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: linear-gradient(135deg, #667eea, #764ba2);
            }}
            
            .chart-img {{
                max-width: 100%;
                border-radius: 12px;
                display: block;
                margin: 0 auto 20px auto;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
                transition: transform 0.3s ease;
            }}
            
            .chart-img:hover {{
                transform: scale(1.02);
            }}
            
            .chart-explain {{
                color: #555;
                font-size: 1.1em;
                background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%);
                border-radius: 12px;
                padding: 20px;
                border-left: 4px solid #667eea;
                line-height: 1.8;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }}
            
            .footer {{
                text-align: center;
                color: #888;
                font-size: 0.95em;
                margin-top: 50px;
                padding-top: 30px;
                border-top: 2px solid #eee;
                background: linear-gradient(90deg, transparent, #f0f0f0, transparent);
                padding: 20px;
                border-radius: 10px;
            }}
            
            .stats {{
                display: flex;
                justify-content: space-around;
                margin: 30px 0;
                flex-wrap: wrap;
            }}
            
            .stat-item {{
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%);
                border-radius: 12px;
                margin: 10px;
                min-width: 150px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }}
            
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
                display: block;
            }}
            
            .stat-label {{
                color: #666;
                font-size: 0.9em;
                margin-top: 5px;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    margin: 10px;
                    padding: 20px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .stats {{
                    flex-direction: column;
                }}
            }}
            
            /* 添加一些动画效果 */
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .chart-block {{
                animation: fadeInUp 0.6s ease-out;
            }}
            
            .chart-block:nth-child(2) {{ animation-delay: 0.1s; }}
            .chart-block:nth-child(3) {{ animation-delay: 0.2s; }}
            .chart-block:nth-child(4) {{ animation-delay: 0.3s; }}
            .chart-block:nth-child(5) {{ animation-delay: 0.4s; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 数据分析报告</h1>
                <div class="subtitle">专业的数据洞察与可视化分析</div>
            </div>
            
            <div class="summary">
                <strong>🎯 综合结论</strong>
                {summary}
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{len(all_img_paths)}</span>
                    <div class="stat-label">生成图表</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(all_explanations)}</span>
                    <div class="stat-label">分析解读</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{datetime.datetime.now().strftime('%m/%d')}</span>
                    <div class="stat-label">生成日期</div>
                </div>
            </div>
            
            {img_html}
            
            <div class="footer">
                <strong>📅 报告生成时间：{now}</strong><br>
                <em>由AI智能分析系统生成</em>
            </div>
        </div>
    </body>
    </html>
    """
    os.makedirs(os.path.join(os.path.dirname(__file__), "reports"), exist_ok=True)
    output_path = os.path.join(
        os.path.dirname(__file__), "reports", f"analysis_report_{now}.html"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    1. 如果收到文件且用户消息包含“分析”，则：
        a) 自动生成图表
        b) 对每个图表用AI进行解释，输出
        c) 汇总所有解释，再进行一次整体分析
    2. 如果没有收到文件，则正常走原有AI问答流程。
    """
    file_elements = [e for e in message.elements if getattr(e, "type", None) == "file"]
    user_content = message.content.strip()

    # 分析流程：有文件且用户消息包含“分析”
    if file_elements and (
        "分析" in user_content or "分析下" in user_content or "分析一下" in user_content
    ):
        all_explanations = []
        all_img_paths = []
        for file_element in file_elements:
            file_path = file_element.path
            file_extension = os.path.splitext(file_path)[1].lower()

            # 检查文件格式
            if file_extension not in [".csv", ".xlsx", ".xls"]:
                await cl.Message(
                    content=f"❌ 不支持的文件格式: {file_extension}\n"
                    f"请上传CSV(.csv)或Excel(.xlsx/.xls)文件。"
                ).send()
                continue

            try:
                img_paths = generate_charts(file_path)
                all_img_paths.extend(img_paths)
            except Exception as e:
                await cl.Message(
                    content=f"❌ 处理文件时出错: {str(e)}\n"
                    f"请确保文件格式正确且数据完整。"
                ).send()
                continue
            # 针对每个图表，先展示再解释
            for img_path in img_paths:
                await cl.Message(
                    content=f"自动生成的图表：",
                    elements=[cl.Image(name=os.path.basename(img_path), path=img_path)],
                ).send()
                with open(img_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                image_url = f"data:image/png;base64,{encoded_string}"
                explain_prompt = [
                    {
                        "role": "system",
                        "content": "你是一个数据分析专家，请根据用户上传的图表图片，给出简明的中文解读。",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"请分析下这张图表："},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    },
                ]
                response = await client.chat.completions.create(
                    model=AZURE_DEPLOYMENT_NAME,
                    messages=explain_prompt,
                )
                explanation = response.choices[0].message.content
                all_explanations.append(explanation)
                await cl.Message(content=f"图表解读：{explanation}").send()
        # 汇总所有解释，再进行一次整体分析
        summary_prompt = [
            {
                "role": "system",
                "content": "你是一个数据分析专家，请根据以下所有图表的解读，给出整体数据分析结论。",
            },
            {"role": "user", "content": "\n".join(all_explanations)},
        ]
        summary_response = await client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=summary_prompt,
        )
        summary = summary_response.choices[0].message.content
        await cl.Message(content=f"整体分析结论：{summary}").send()
        # 生成HTML报告并发送下载链接
        report_path = generate_html_report(all_img_paths, all_explanations, summary)
        await cl.Message(
            content=f"🎉分析报告已生成！点击下载报告",
            elements=[cl.File(name="analysis_report.html", path=report_path)],
        ).send()
    else:
        # 没有文件，正常AI问答
        response = await client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[
                {
                    "content": "You are an agent that can help with data analysis and visualization.",
                    "role": "system",
                },
                {"content": user_content, "role": "user"},
            ],
        )
        await cl.Message(content=response.choices[0].message.content).send()

import chainlit as cl
import pandas as pd
from config import gpt_client, AZURE_DEPLOYMENT_NAME
import os
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.family"] = "SimHei"  # 设置中文字体
matplotlib.rcParams["axes.unicode_minus"] = False  # 正常显示负号
import seaborn as sns
import uuid
import base64
import datetime

client = gpt_client

# Instrument the OpenAI client
cl.instrument_openai()


# 自动生成图表并保存为图片，返回图片路径列表
@cl.step(type="tool")
def generate_charts(file_path, output_dir="charts"):
    df = pd.read_csv(file_path)
    img_paths = []
    os.makedirs(output_dir, exist_ok=True)

    # 1. 柱状图/条形图：分类变量的计数
    for col in df.select_dtypes(include=["object", "category"]):
        if df[col].nunique() < 20:
            plt.figure()
            df[col].value_counts().plot(kind="bar")
            plt.title(f"{col} 分布")
            plt.xlabel(col)
            plt.ylabel("计数")
            plt.tight_layout()
            img_path = os.path.join(output_dir, f"{col}_bar_{uuid.uuid4().hex[:8]}.png")
            plt.savefig(img_path)
            plt.close()
            img_paths.append(img_path)

    # 2. 数值型变量的直方图
    for col in df.select_dtypes(include=["number"]):
        plt.figure()
        df[col].hist(bins=20)
        plt.title(f"{col} 分布")
        plt.xlabel(col)
        plt.ylabel("频数")
        plt.tight_layout()
        img_path = os.path.join(output_dir, f"{col}_hist_{uuid.uuid4().hex[:8]}.png")
        plt.savefig(img_path)
        plt.close()
        img_paths.append(img_path)

    # 3. 数值型变量之间的散点图（只画前两个数值型变量）
    num_cols = df.select_dtypes(include=["number"]).columns
    if len(num_cols) >= 2:
        plt.figure()
        sns.scatterplot(x=df[num_cols[0]], y=df[num_cols[1]])
        plt.title(f"{num_cols[0]} vs {num_cols[1]}")
        plt.tight_layout()
        img_path = os.path.join(output_dir, f"scatter_{uuid.uuid4().hex[:8]}.png")
        plt.savefig(img_path)
        plt.close()
        img_paths.append(img_path)

    # 4. 如果有时间序列，画折线图
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
                plt.figure()
                for num_col in num_cols:
                    plt.plot(df[col], df[num_col], label=num_col)
                plt.title(f"{col} 时间序列")
                plt.xlabel(col)
                plt.ylabel("数值")
                plt.legend()
                plt.tight_layout()
                img_path = os.path.join(
                    output_dir, f"{col}_line_{uuid.uuid4().hex[:8]}.png"
                )
                plt.savefig(img_path)
                plt.close()
                img_paths.append(img_path)
            except Exception:
                continue

    # 5. 箱线图（Boxplot）
    for col in df.select_dtypes(include=["number"]):
        plt.figure()
        sns.boxplot(y=df[col])
        plt.title(f"{col} 箱线图")
        plt.tight_layout()
        img_path = os.path.join(output_dir, f"{col}_box_{uuid.uuid4().hex[:8]}.png")
        plt.savefig(img_path)
        plt.close()
        img_paths.append(img_path)

    # 6. 热力图（相关性）
    if len(num_cols) >= 2:
        plt.figure(figsize=(8, 6))
        corr = df[num_cols].corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm")
        plt.title("数值型变量相关性热力图")
        plt.tight_layout()
        img_path = os.path.join(output_dir, f"heatmap_{uuid.uuid4().hex[:8]}.png")
        plt.savefig(img_path)
        plt.close()
        img_paths.append(img_path)

    # 7. 饼图（Pie chart）
    for col in df.select_dtypes(include=["object", "category"]):
        if df[col].nunique() < 10:
            plt.figure()
            df[col].value_counts().plot.pie(autopct="%1.1f%%")
            plt.title(f"{col} 占比")
            plt.ylabel("")
            plt.tight_layout()
            img_path = os.path.join(output_dir, f"{col}_pie_{uuid.uuid4().hex[:8]}.png")
            plt.savefig(img_path)
            plt.close()
            img_paths.append(img_path)

    # 8. 成对关系图（Pairplot）
    if len(num_cols) >= 2:
        pairplot = sns.pairplot(df[num_cols])
        pairplot.fig.suptitle("数值型变量成对关系", y=1.02)
        img_path = os.path.join(output_dir, f"pairplot_{uuid.uuid4().hex[:8]}.png")
        pairplot.savefig(img_path)
        plt.close()
        img_paths.append(img_path)

    return img_paths


def generate_html_report(
    img_paths, explanations, summary, output_path="analysis_report.html"
):
    # 图片转base64
    img_html = ""
    for img_path, explain in zip(img_paths, explanations):
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        img_html += f"""
        <div class="chart-block">
            <img src="data:image/png;base64,{img_b64}" class="chart-img"/>
            <div class="chart-explain">{explain}</div>
        </div>
        """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>数据分析报告</title>
        <style>
            body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f7fa; color: #222; }}
            .container {{ max-width: 900px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px #ccc; padding: 32px; }}
            h1 {{ text-align: center; color: #2b6cb0; }}
            .summary {{ background: #e6f7ff; border-left: 6px solid #1890ff; padding: 16px; margin-bottom: 32px; border-radius: 8px; }}
            .chart-block {{ margin-bottom: 36px; background: #f9f9f9; border-radius: 8px; padding: 16px; box-shadow: 0 1px 4px #eee; }}
            .chart-img {{ max-width: 100%; border-radius: 6px; display: block; margin: 0 auto 12px auto; }}
            .chart-explain {{ color: #444; font-size: 1.05em; background: #f0f5ff; border-radius: 6px; padding: 10px; }}
            .footer {{ text-align: right; color: #888; font-size: 0.95em; margin-top: 40px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>数据分析报告</h1>
            <div class="summary">
                <strong>综合结论：</strong><br>
                {summary}
            </div>
            {img_html}
            <div class="footer">报告生成时间：{now}</div>
        </div>
    </body>
    </html>
    """
    os.makedirs(os.path.join(os.path.dirname(__file__), "reports"), exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
            img_paths = generate_charts(file_path)
            all_img_paths.extend(img_paths)
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
            content=f"🎉 <b>分析报告已生成！</b> <br> <a href='{report_path}' download>点击下载报告</a>",
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

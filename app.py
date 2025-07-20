from sanic import Sanic, Request, response
from sanic.response import json, file
import os
from dotenv import load_dotenv

load_dotenv()
import sys
import tempfile
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入分析模块
from core.analysis import generate_html_from_excel

app = Sanic("app")

# 配置上传文件大小限制 (50MB)
app.config.REQUEST_MAX_SIZE = 50 * 1024 * 1024

# 配置请求超时时间 (5分钟)
app.config.REQUEST_TIMEOUT = 300
app.config.RESPONSE_TIMEOUT = 300


@app.route("/", methods=["GET"])
async def index(request: Request):
    """API首页"""
    return json(
        {
            "message": "Excel分析API服务",
            "version": "1.0.0",
            "endpoints": {
                "/analyze": "POST - 上传Excel文件进行分析 (参数: file, uid可选)",
                "/analyze/download": "POST - 上传Excel文件并返回下载链接 (参数: file, uid可选)",
                "/download/<filename>": "GET - 下载生成的报告",
                "/health": "GET - 健康检查",
            },
        }
    )


@app.route("/health", methods=["GET"])
async def health_check(request: Request):
    """健康检查接口"""
    return json(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "data-analysis-api",
        }
    )


@app.route("/analyze", methods=["POST"])
async def analyze_excel(request: Request):
    """
    分析Excel文件接口

    请求参数:
    - file: Excel文件 (.xlsx 或 .xls)
    - uid: 用户ID（可选，用于区分不同的聊天会话，如果不提供将自动生成）

    返回:
    - 成功: HTML分析报告文件
    - 失败: 错误信息
    """
    try:
        # 检查是否有文件上传
        if not request.files:
            return json(
                {"error": "没有上传文件", "message": "请上传Excel文件(.xlsx或.xls)"},
                status=400,
            )

        # 获取上传的文件
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return json(
                {"error": "文件参数错误", "message": "请使用'file'参数上传Excel文件"},
                status=400,
            )

        # 检查文件扩展名
        filename = uploaded_file.name
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension not in [".xlsx", ".xls"]:
            return json(
                {
                    "error": "不支持的文件格式",
                    "message": "只支持Excel文件格式(.xlsx或.xls)",
                },
                status=400,
            )

        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as temp_file:
            # 写入上传的文件内容
            temp_file.write(uploaded_file.body)
            temp_file_path = temp_file.name

        try:
            # 获取uid参数（可选），如果没有则生成一个
            uid = request.form.get("uid") if request.form else None
            if not uid:
                import uuid

                uid = f"user_{uuid.uuid4().hex[:8]}"
                print(f"Generated uid: {uid}")

            # 使用demo.py中的函数生成HTML报告
            html_report_path = await generate_html_from_excel(temp_file_path, uid)

            # 读取生成的HTML文件
            with open(html_report_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # 获取文件名
            report_filename = os.path.basename(html_report_path)

            # 返回HTML文件
            return response.html(
                html_content,
                headers={
                    "Content-Disposition": f'attachment; filename="{report_filename}"',
                    "Content-Type": "text/html; charset=utf-8",
                },
            )

        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        # 记录错误日志
        print(f"分析Excel文件时出错: {str(e)}")

        return json(
            {"error": "分析失败", "message": f"处理文件时发生错误: {str(e)}"},
            status=500,
        )


@app.route("/analyze/download", methods=["POST"])
async def analyze_excel_download(request: Request):
    """
    分析Excel文件并返回下载链接

    请求参数:
    - file: Excel文件 (.xlsx 或 .xls)
    - uid: 用户ID（可选，用于区分不同的聊天会话，如果不提供将自动生成）

    返回:
    - 成功: 下载链接
    - 失败: 错误信息
    """
    try:
        # 检查是否有文件上传
        if not request.files:
            return json(
                {"error": "没有上传文件", "message": "请上传Excel文件(.xlsx或.xls)"},
                status=400,
            )

        # 获取上传的文件
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return json(
                {"error": "文件参数错误", "message": "请使用'file'参数上传Excel文件"},
                status=400,
            )

        # 检查文件扩展名
        filename = uploaded_file.name
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension not in [".xlsx", ".xls"]:
            return json(
                {
                    "error": "不支持的文件格式",
                    "message": "只支持Excel文件格式(.xlsx或.xls)",
                },
                status=400,
            )

        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as temp_file:
            # 写入上传的文件内容
            temp_file.write(uploaded_file.body)
            temp_file_path = temp_file.name

        try:
            # 获取uid参数（可选），如果没有则生成一个
            uid = request.form.get("uid") if request.form else None
            if not uid:
                import uuid

                uid = f"user_{uuid.uuid4().hex[:8]}"
                print(f"Generated uid: {uid}")

            # 使用demo.py中的函数生成HTML报告
            html_report_path = await generate_html_from_excel(temp_file_path, uid)

            # 获取文件名
            report_filename = os.path.basename(html_report_path)

            # 返回下载链接信息
            return json(
                {
                    "success": True,
                    "message": "分析完成",
                    "download_url": f"/download/{report_filename}",
                    "filename": report_filename,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        # 记录错误日志
        print(f"分析Excel文件时出错: {str(e)}")

        return json(
            {"error": "分析失败", "message": f"处理文件时发生错误: {str(e)}"},
            status=500,
        )


@app.route("/download/<filename:path>", methods=["GET"])
async def download_report(request: Request, filename: str):
    """
    下载生成的HTML报告

    参数:
    - filename: 报告文件名
    """
    try:
        # 构建报告文件路径 - 修复路径问题
        current_dir = os.path.dirname(os.path.abspath(__file__))
        reports_dir = os.path.join(current_dir, "reports")
        file_path = os.path.join(reports_dir, filename)

        print(f"Looking for file: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        print(f"Current directory: {current_dir}")
        print(f"Reports directory: {reports_dir}")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            return json(
                {"error": "文件不存在", "message": f"报告文件 {filename} 不存在"},
                status=404,
            )

        # 返回文件
        return await file(file_path, filename=filename)

    except Exception as e:
        print(f"下载文件时出错: {str(e)}")
        return json(
            {"error": "下载失败", "message": f"下载文件时发生错误: {str(e)}"},
            status=500,
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    # 启动服务器
    app.run(host=host, port=port, debug=False, access_log=True)

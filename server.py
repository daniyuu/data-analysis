import os
from dotenv import load_dotenv

load_dotenv()
from app import app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    # 启动服务器
    app.run(host=host, port=port, debug=False, access_log=True)

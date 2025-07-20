import requests
import time
from datetime import datetime


def test_azure_api(host):
    """Test the Azure API with detailed debugging"""
    base_url = host
    # base_url = (
    #     "https://data-analysis-0719-crhmezfyhmfwcjhq.canadacentral-01.azurewebsites.net"
    # )

    print("Testing Azure API Server")
    print("=" * 50)

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Health check failed: {e}")
        return

    # Test root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Root endpoint failed: {e}")

    # Test analyze endpoint with GET (should fail)
    print("\n3. Testing analyze endpoint with GET (should fail)...")
    try:
        response = requests.get(f"{base_url}/analyze", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   GET analyze failed: {e}")

    # Test analyze endpoint with POST (should work)
    print("\n4. Testing analyze endpoint with POST...")
    try:
        with open("examples/授信数据mock.xlsx", "rb") as file:
            files = {
                "file": (
                    "授信数据mock.xlsx",
                    file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }

            print("   Sending POST request to /analyze...")
            response = requests.post(f"{base_url}/analyze", files=files, timeout=300)

            print(f"   Status Code: {response.status_code}")
            print(
                f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}"
            )

            if response.status_code == 200:
                print("   ✅ POST analyze successful!")
                print(f"   Response size: {len(response.text)} characters")
            elif response.status_code == 405:
                print("   ❌ 405 Method Not Allowed")
                print(f"   Response: {response.text[:200]}")
                print("   This suggests the endpoint exists but doesn't accept POST")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"   POST analyze failed: {e}")

    # Test analyze/download endpoint
    print("\n5. Testing analyze/download endpoint...")
    try:
        with open("examples/授信数据mock.xlsx", "rb") as file:
            files = {
                "file": (
                    "授信数据mock.xlsx",
                    file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }

            print("   Sending POST request to /analyze/download...")
            response = requests.post(
                f"{base_url}/analyze/download", files=files, timeout=300
            )

            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                try:
                    json_response = response.json()
                    print("   ✅ Download endpoint successful!")
                    print(f"   Message: {json_response.get('message')}")
                    print(f"   Download URL: {json_response.get('download_url')}")
                except Exception as e:
                    print(f"   JSON decode error: {e}")
                    print(f"   Response: {response.text[:200]}")
            elif response.status_code == 405:
                print("   ❌ 405 Method Not Allowed")
                print(f"   Response: {response.text[:200]}")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"   Download endpoint failed: {e}")

    print("\n" + "=" * 50)
    print("Test completed!")


def test_analyze_by_file_url(host):
    """测试通过文件URL分析Excel文件"""
    url = f"{host}/analyze_by_file_url"

    # 使用一个公开的Excel文件URL进行测试
    # 这里使用一个示例URL，实际使用时需要替换为真实的Excel文件URL
    json_data = {
        "file_url": "https://raw.githubusercontent.com/pandas-dev/pandas/main/pandas/tests/io/data/excel/test1.xlsx",
        "file_name": "test1.xlsx",  # 确保文件名包含正确的扩展名
        "uid": "test_user_123",
    }

    try:
        # 发送JSON格式的请求
        response = requests.post(
            url, json=json_data, headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            # 保存返回的HTML文件
            filename = (
                f"report_from_url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"HTML报告已保存为: {filename}")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"测试失败: {str(e)}")


if __name__ == "__main__":
    host = "http://localhost:8000"
    # host = (
    #     "https://data-analysis-0719-crhmezfyhmfwcjhq.canadacentral-01.azurewebsites.net"
    # )
    # test_azure_api(host)

    # 测试新的 analyze_by_file_url 接口
    print("\n" + "=" * 50)
    print("Testing analyze_by_file_url endpoint...")
    test_analyze_by_file_url(host)

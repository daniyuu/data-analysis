import requests
import time


def test_local_api():
    """Test the local API with better progress indication"""
    # base_url = "http://localhost:8000"
    base_url = (
        "http://data-analysis-0719-crhmezfyhmfwcjhq.canadacentral-01.azurewebsites.net"
    )

    print("Testing Local API Server")
    print("=" * 50)

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return

    # Test analyze endpoint
    print("\n2. Testing analyze endpoint (HTML response)...")
    print("   This will take 30-60 seconds...")

    try:
        with open("examples/授信数据mock.xlsx", "rb") as file:
            files = {
                "file": (
                    "授信数据mock.xlsx",
                    file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }

            start_time = time.time()
            response = requests.post(
                f"{base_url}/analyze", files=files, timeout=300
            )  # 5分钟超时
            end_time = time.time()

            print(f"   Request completed in {end_time - start_time:.1f} seconds")
            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                print("✅ Analyze endpoint successful!")
                print(f"   Response size: {len(response.text)} characters")

                # Save the HTML report
                with open("local_report.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("   HTML report saved as: local_report.html")
            else:
                print(f"❌ Analyze endpoint failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

    except requests.exceptions.Timeout:
        print("❌ Request timed out (took longer than 5 minutes)")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Test analyze/download endpoint
    print("\n3. Testing analyze/download endpoint (JSON response)...")
    print("   This will take 30-60 seconds...")

    try:
        with open("examples/授信数据mock.xlsx", "rb") as file:
            files = {
                "file": (
                    "授信数据mock.xlsx",
                    file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }

            start_time = time.time()
            response = requests.post(
                f"{base_url}/analyze/download", files=files, timeout=300
            )  # 5分钟超时
            end_time = time.time()

            print(f"   Request completed in {end_time - start_time:.1f} seconds")
            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                try:
                    json_response = response.json()
                    print("✅ Download endpoint successful!")
                    print(f"   Message: {json_response.get('message')}")
                    print(f"   Download URL: {json_response.get('download_url')}")
                    print(f"   Filename: {json_response.get('filename')}")

                    # Try to download the report
                    if json_response.get("download_url"):
                        print("   Downloading the report...")
                        download_response = requests.get(
                            f"{base_url}{json_response['download_url']}", timeout=30
                        )
                        if download_response.status_code == 200:
                            with open(
                                "download_report.html", "w", encoding="utf-8"
                            ) as f:
                                f.write(download_response.text)
                            print("   Downloaded report saved as: download_report.html")
                        else:
                            print(
                                f"   Failed to download report: {download_response.status_code}"
                            )
                            print(
                                f"   Download response: {download_response.text[:200]}..."
                            )

                except requests.exceptions.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Download endpoint failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

    except requests.exceptions.Timeout:
        print("❌ Request timed out (took longer than 5 minutes)")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    test_local_api()

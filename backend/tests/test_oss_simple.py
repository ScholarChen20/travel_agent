"""
简单的OSS上传测试脚本
快速验证OSS配置是否正确
"""

import sys
from pathlib import Path
import io
from PIL import Image

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from ..app.config import get_settings

try:
    import alibabacloud_oss_v2 as oss
    from alibabacloud_oss_v2.models import PutObjectRequest
except ImportError:
    print("❌ 请先安装OSS SDK: pip install alibabacloud-oss-v2")
    sys.exit(1)


def main():
    """主函数"""
    # 1. 读取配置
    settings = get_settings()

    print("\n" + "="*50)
    print("OSS 配置信息")
    print("="*50)
    print(f"AccessKeyId: {settings.oss_access_key_id[:8]}***")
    print(f"Endpoint: {settings.oss_endpoint}")
    print(f"Bucket: {settings.oss_bucket_name}")
    print("="*50 + "\n")

    # 2. 创建OSS客户端
    print("初始化OSS客户端...")
    try:
        # 使用静态凭证认证
        credentials_provider = oss.credentials.StaticCredentialsProvider(
            access_key_id=settings.oss_access_key_id,
            access_key_secret=settings.oss_access_key_secret
        )
        config = oss.config.load_default()
        config.credentials_provider = credentials_provider
        config.endpoint = settings.oss_endpoint
        config.region = settings.region
        client = oss.Client(config)
        print("✅ OSS客户端初始化成功\n")

    except Exception as e:
        print(f"❌ OSS客户端初始化失败: {str(e)}")
        return

    # 3. 创建测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_data = img_buffer.getvalue()

    # 4. 上传到 OSS
    object_name = "test.jpg"  # ⚠️ 极简 key，避免任何路径或特殊字符
    print(f"📤 上传 Object Key: {object_name!r}")

    try:
        request = PutObjectRequest(
            bucket=settings.oss_bucket_name,
            key=object_name,
            body=img_data
        )
        response = client.put_object(request)
        print("✅ 上传成功!",response)

        # 生成可访问 URL
        url = f"https://{settings.oss_bucket_name}.{settings.oss_endpoint}/{object_name}"
        print(f"🔗 访问链接: {url}")

    except Exception as e:
        print(f"❌ 上传失败: {e}")
        import traceback
        traceback.print_exc()

def test():
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider

    # 加载SDK的默认配置，并设置凭证提供者
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider

    # 方式一：只填写Region（推荐）
    # 必须指定Region ID，以华东1（杭州）为例，Region填写为cn-hangzhou，SDK会根据Region自动构造HTTPS访问域名
    cfg.region = 'cn-hangzhou'

    # # 方式二：同时填写Region和Endpoint
    # # 必须指定Region ID，以华东1（杭州）为例，Region填写为cn-hangzhou
    # cfg.region = 'cn-hangzhou'
    # # 填写Bucket所在地域对应的公网Endpoint。以华东1（杭州）为例，Endpoint填写为'https://oss-cn-hangzhou.aliyuncs.com'
    # cfg.endpoint = 'https://oss-cn-hangzhou.aliyuncs.com'

    # 使用配置好的信息创建OSS客户端
    client = oss.Client(cfg)

    # 定义要上传的字符串内容
    text_string = "Hello, OSS!"
    data = text_string.encode('utf-8')  # 将字符串编码为UTF-8字节串

    # 执行上传对象的请求，指定存储空间名称、对象名称和数据内容
    result = client.put_object(oss.PutObjectRequest(
        bucket="java-webai-1",
        key="exampledir/exampleobject.txt",
        body=data,
    ))

    # 输出请求的结果状态码、请求ID、ETag，用于检查请求是否成功
    print(f'status code: {result.status_code}\n'
          f'request id: {result.request_id}\n'
          f'etag: {result.etag}'
    )


if __name__ == "__main__":
    main()

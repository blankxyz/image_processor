from collections.abc import Generator
from typing import Any
from PIL import Image, ImageOps
import io
import uuid
import datetime
import requests
import base64
from urllib.parse import urlparse

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

class ImageProcessorTool(Tool):
    def resize_image_to_1080p(self, image_file: bytes, resize_method: str = "fit",
                            quality: int = 90, output_format: str = "jpeg") -> dict[str, str | int | bytes]:
        """
        将图片调整到1080p分辨率

        :param image_file: 图片文件的字节流
        :param resize_method: 调整方法 ("fit", "crop", "stretch")
        :param quality: 压缩质量（1-100），默认 90
        :param output_format: 输出格式 ("jpeg", "png", "webp")
        :return: 调整后的图片信息字典，包含文件内容、格式、大小和生成的唯一文件名
        """
        try:
            # 打开图片
            with Image.open(io.BytesIO(image_file)) as img:
                print("Image resize to 1080p started")

                # 自动纠正图片方向
                img = ImageOps.exif_transpose(img)

                # 获取原始尺寸
                original_width, original_height = img.size
                print(f"Original image size: {original_width}x{original_height}")

                # 目标尺寸 (1920x1080)
                target_width, target_height = 1080, 720

                # 根据方法调整尺寸
                if resize_method == "fit":
                    # 保持比例，适应1080p边界
                    img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                    resized_img = img
                    final_width, final_height = resized_img.size
                elif resize_method == "crop":
                    # 裁剪到精确1080p尺寸
                    resized_img = ImageOps.fit(
                        img, (target_width, target_height), Image.Resampling.LANCZOS
                    )
                    final_width, final_height = target_width, target_height
                elif resize_method == "stretch":
                    # 拉伸到1080p（可能变形）
                    resized_img = img.resize(
                        (target_width, target_height), Image.Resampling.LANCZOS
                    )
                    final_width, final_height = target_width, target_height
                else:
                    raise ValueError(f"Unsupported resize method: {resize_method}")

                # 生成唯一的文件名
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"1080p_{resize_method}_{timestamp}_{unique_id}.{output_format}"

                # 转换颜色模式以支持不同输出格式
                if output_format == 'jpeg':
                    # JPEG需要RGB模式
                    if resized_img.mode in ('RGBA', 'LA', 'P'):
                        # 创建白色背景
                        background = Image.new('RGB', resized_img.size, (255, 255, 255))
                        if resized_img.mode == 'P':
                            resized_img = resized_img.convert('RGBA')
                        if resized_img.mode == 'RGBA':
                            background.paste(resized_img, mask=resized_img.split()[-1])
                        else:
                            background.paste(resized_img)
                        resized_img = background
                    elif resized_img.mode != 'RGB':
                        resized_img = resized_img.convert('RGB')
                elif output_format == 'png':
                    # PNG支持RGBA
                    if resized_img.mode not in ('RGB', 'RGBA'):
                        resized_img = resized_img.convert('RGBA')
                elif output_format == 'webp':
                    # WebP支持RGB和RGBA
                    if resized_img.mode not in ('RGB', 'RGBA'):
                        resized_img = resized_img.convert('RGB')

                # 创建字节流缓冲区
                output = io.BytesIO()

                # 保存调整后的图片到缓冲区
                save_kwargs = {'format': output_format.upper()}

                if output_format == 'jpeg':
                    save_kwargs.update({'quality': quality, 'optimize': True})
                elif output_format == 'png':
                    save_kwargs.update({'optimize': True})
                elif output_format == 'webp':
                    save_kwargs.update({'quality': quality, 'method': 6})

                resized_img.save(output, **save_kwargs)
                output.seek(0)

                print(f"Image resized successfully: {final_width}x{final_height}")

                return {
                    "file": output.read(),
                    "format": output_format.upper(),
                    "size": len(output.getvalue()),
                    "filename": filename,
                    "dimensions": f"{final_width}x{final_height}",
                    "original_size": f"{original_width}x{original_height}",
                    "method": resize_method
                }
        except Exception as e:
            raise ValueError(f"Image resize failed: {str(e)}")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        imgs = tool_parameters.get("input_image")
        host_url = tool_parameters.get("host_url")
        resize_method = tool_parameters.get("resize_method", "fit")
        quality = tool_parameters.get("quality", 90)
        output_format = tool_parameters.get("output_format", "jpeg")

        if not imgs:
            yield self.create_json_message({
                "result": "请提供图片文件"
            })
            return

        if not isinstance(imgs, list):
            yield self.create_json_message({
                "result": "请提供图片文件列表"
            })
            return

        # 验证参数
        if resize_method not in ['fit', 'crop', 'stretch']:
            yield self.create_json_message({
                "result": "错误：无效的调整方法，请选择 fit、crop 或 stretch"
            })
            return

        if not (1 <= quality <= 100):
            yield self.create_json_message({
                "result": "错误：质量参数必须在1-100之间"
            })
            return

        if output_format not in ['jpeg', 'png', 'webp']:
            yield self.create_json_message({
                "result": "错误：不支持的输出格式，请选择 jpeg、png 或 webp"
            })
            return

        for img in imgs:
            # 获取正确的字节流数据
            if isinstance(img, File):
                try:
                    # 先判断File mime 是否为图片类型
                    if img.mime_type not in ["image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"]:
                        yield self.create_json_message({
                            "result": f"不支持的文件类型: {img.mime_type}"
                        })
                        continue
                    url = img.url
                    if not url.startswith(('http://', 'https://')):
                        # 去掉末尾的斜杠
                        host_url = host_url.rstrip('/')
                        url = f"{host_url}/{url}"
                    # 下载图片
                    response = requests.get(url)
                    response.raise_for_status()
                    input_image_bytes = response.content
                    print(f"Downloaded image from: {url}")
                except Exception as e:
                    yield self.create_json_message({
                        "result": f"下载图片失败: {str(e)}"
                    })
                    continue
            elif isinstance(img, bytes):
                input_image_bytes = img
            else:
                yield self.create_json_message({
                    "result": f"不支持的图片格式: {type(img)}"
                })
                continue

            try:
                # 调整图片到1080p
                resized_img = self.resize_image_to_1080p(
                    input_image_bytes,
                    resize_method=resize_method,
                    quality=quality,
                    output_format=output_format
                )

                # 创建元数据
                meta = {
                    "filename": resized_img.get("filename", "resized_1080p.jpg"),
                    "mime_type": f"image/{resized_img.get('format').lower()}" if resized_img.get('format') else img.mime_type if isinstance(img, File) else "image/jpeg",
                    "size": resized_img.get("size"),
                }

                # 输出处理结果信息
                result_info = (
                    f"✅ 图片已成功调整为1080p!\n"
                    f"📐 调整方法: {self._get_method_description(resize_method)}\n"
                    f"📏 原始尺寸: {resized_img.get('original_size')}\n"
                    f"📏 新尺寸: {resized_img.get('dimensions')}\n"
                    f"🎨 输出格式: {output_format.upper()}\n"
                    f"📊 质量设置: {quality}\n"
                    f"📦 文件大小: {resized_img.get('size') / (1024*1024):.2f} MB\n"
                    f"📁 文件名: {resized_img.get('filename')}"
                )

                yield self.create_json_message({
                    "result": result_info
                })

                # 输出调整后的图片文件
                yield self.create_blob_message(resized_img.get("file"), meta)

            except Exception as e:
                yield self.create_json_message({
                    "result": f"处理图片时发生错误: {str(e)}"
                })
                continue

    def _get_method_description(self, method: str) -> str:
        """获取调整方法的描述"""
        descriptions = {
            'fit': '适应 (保持宽高比)',
            'crop': '裁剪 (精确尺寸)',
            'stretch': '拉伸 (可能变形)'
        }
        return descriptions.get(method, method)
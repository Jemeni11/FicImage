import PIL
from PIL import Image
from io import BytesIO
from base64 import b64decode
import math
import requests
from typing import Tuple


def get_image_from_url(
		url: str,
		image_format: str,
		compress_images: bool,
		max_image_size: int,
		debug: bool
) -> Tuple[bytes, str, str]:
	"""
	:param url: The url of the image.
	:param image_format: The format to convert the image to.
	:param compress_images: Whether to compress the image or not.
	:param max_image_size: The maximum size of the image in bytes.
	:param debug: Whether to print debug messages or not.
	:return: A tuple of the image data, the image format and the image mime type.
	"""
	try:
		if url.startswith("data:image") and 'base64' in url:
			if debug:
				print("Base64 image detected")
			head, base64data = url.split(',')
			file_ext = str(head.split(';')[0].split('/')[1])
			imgdata = b64decode(base64data)
			
			if file_ext.lower() in ("gif", "webp", "svg"):
				if debug:
					print("GIF/WEBP/SVG image detected, skipping compression")
				return imgdata, file_ext, f"image/{file_ext}"
			
			elif file_ext.lower() not in ["jpg", "jpeg", "png", "gif", "webp", "svg"]:
				if debug:
					print(f"Image format {file_ext} not supported, converting to {image_format}")
				return (
					_convert_to_new_format(imgdata, image_format, debug).read(),
					image_format.lower(),
					f"image/{image_format.lower()}"
				)
			
			if compress_images:
				compressed_base64_image = compress_image(BytesIO(imgdata), max_image_size, file_ext, debug)
				imgdata = PIL_Image_to_bytes(compressed_base64_image, file_ext)
				
			return imgdata, file_ext, f"image/{file_ext}"
		
		with requests.Session() as session:
			img = session.get(url, stream=True)
		
			if img.headers.get("content-type", "") == "image/svg+xml":
				return img.content, "svg", "image/svg+xml"
			
			image = BytesIO(img.content)
			image.seek(0)
	
			PIL_image = Image.open(image)
			img_format = str(PIL_image.format)
	
			if img_format.lower() in ("gif", "webp"):
				PIL_image = Image.open(image)
				if img_format.lower() == "gif":
					if PIL_image.info['version'] not in [b"GIF89a", "GIF89a"]:
						PIL_image.info['version'] = b"GIF89a"
					return PIL_Image_to_bytes(PIL_image, "GIF"), "gif", "image/gif"
				return PIL_Image_to_bytes(PIL_image, "WEBP"), "webp", "image/webp"
	
			if compress_images:
				PIL_image = compress_image(image, max_image_size, img_format, debug)
	
			return PIL_Image_to_bytes(PIL_image, image_format), image_format, f"image/{image_format.lower()}"

	except Exception as e:
		print("Encountered an error downloading image: " + str(e))


def compress_image(image: BytesIO, target_size: int, image_format: str, debug: bool) -> PIL.Image.Image:
	image_size = get_size_format(len(image.getvalue()))
	if debug:
		print(f"Image size: {image_size}")

	big_photo = Image.open(image).convert("RGBA")

	target_pixel_count = 2.8114 * target_size
	if len(image.getvalue()) > target_size:
		if debug:
			print(f"Image is greater than {get_size_format(target_size)}, compressing")
		scale_factor = target_pixel_count / math.prod(big_photo.size)
		if scale_factor < 1:
			x, y = tuple(int(scale_factor * dim) for dim in big_photo.size)
			if debug:
				print(f"Resizing image dimensions from {big_photo.size} to ({x}, {y})")
			sml_photo = big_photo.resize((x, y), resample=Image.LANCZOS)
		else:
			sml_photo = big_photo
		compressed_image_size = get_size_format(len(PIL_Image_to_bytes(sml_photo, image_format)))
		if debug:
			print(f"Compressed image size: {compressed_image_size}")
		return sml_photo
	else:
		if debug:
			print(f"Image is less than {get_size_format(target_size)}, not compressing")
		return big_photo


def PIL_Image_to_bytes(
		pil_image: PIL.Image.Image,
		image_format: str
) -> bytes:
	out_io = BytesIO()
	if image_format.lower() in ("gif", "webp"):
		frames = []
		current = pil_image.convert('RGBA')
		while True:
			try:
				frames.append(current)
				pil_image.seek(pil_image.tell() + 1)
				current = Image.alpha_composite(current, pil_image.convert('RGBA'))
			except EOFError:
				break
		frames[0].save(out_io, format=image_format, save_all=True, append_images=frames[1:], optimize=True, loop=0)
		return out_io.getvalue()

	elif image_format.lower() in ["jpeg", "jpg"]:
		# Create a new image with a white background
		background_img = Image.new('RGBA', pil_image.size, "white")

		# Paste the image on top of the background
		background_img.paste(pil_image.convert("RGBA"), (0, 0), pil_image.convert("RGBA"))
		pil_image = background_img.convert('RGB')

	pil_image.save(out_io, format=image_format, optimize=True, quality=95)
	return out_io.getvalue()


def get_size_format(b, factor=1000, suffix="B"):
	"""
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    :param b: The size in bytes.
    :param factor: The factor to divide by.
    :param suffix: The suffix to add to the end.
    """
	for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
		if b < factor:
			return f"{b:.2f}{unit}{suffix}"
		b /= factor
	return f"{b:.2f}Y{suffix}"


def _convert_to_new_format(image_bytestream, image_format: str, debug: bool):
	new_image = BytesIO()
	try:
		Image.open(image_bytestream).save(new_image, format=image_format.upper())
		new_image.name = f'cover.{image_format.lower()}'
		new_image.seek(0)
		return new_image
	except Exception as e:
		if debug:
			print(f"Encountered an error converting image to {image_format}\nError: {e}")
		return image_bytestream

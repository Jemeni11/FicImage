import argparse
import sys
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from .image import get_image_from_url
from .utils import config_check, load_config_json, default_ficimage_settings

__version__ = "2.0.0"


def update_epub(path_to_epub, config_file_path, debug):
	try:
		book = epub.read_epub(path_to_epub)
		print(f'Opened {path_to_epub}')

		# Check if it's a FicHub epub before doing anything else
		# There's no non-tedious way to do this, so we have to check introduction.xhtml
		try:
			is_fichub_epub = False
			for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
				if item.file_name.startswith('introduction'):
					intro_soup = BeautifulSoup(item.content, "lxml-xml")
					intro_p_tags = intro_soup.find_all('p')
					if len(intro_p_tags) != 0:
						intro_p_tag = intro_p_tags[-1]
						# This should give:
						# Exported with the assistance of FicHub.net
						# I could also check intro_p_tag.a
						fichub_attribution_text = intro_p_tag.get_text().replace("\n\t", "")
						if ("FicHub.net" in fichub_attribution_text) \
								or (fichub_attribution_text == "Exported with the assistance of FicHub.net"):
							is_fichub_epub = True
							break
			if is_fichub_epub:
				print("This is a FicHub epub")
			else:
				print("This is not a FicHub epub")
				return

		except Exception as e:
			print("Error! Could not confirm if this is a FicHub epub. Skipping")
			if debug:
				print(f"Error: {e}")
			return

		(config_file_exists, config_file_location) = config_check(config_file_path)
		if config_file_exists:
			ficimage_config = load_config_json(config_file_location)
		else:
			ficimage_config = default_ficimage_settings()
		compress_images_config: bool = ficimage_config.get("compress_images", True)
		default_image_format_config: str = ficimage_config.get("default_image_format", "JPEG")
		if str(default_image_format_config).lower() not in ("jpg", "jpeg", "png"):
			default_image_format_config = "JPEG"
		max_image_size_config: int = ficimage_config.get("max_image_size", 1_000_000)

		file_name = path_to_epub.split('/')[-1].split('.epub')[0]
		images_downloaded = {}

		for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
			try:
				soup = BeautifulSoup(item.content, "lxml-xml")
				p_tags = soup.find_all('p')
				images = [i for i in p_tags if '[img:' in i.text]
				if debug:
					print(f'Found {len(images)} images in {item.file_name}')
				item_file_name = item.file_name.split('.')[0]
				images_downloaded[item.file_name] = [0, len(images)]
				# Clean up the images link
				# Right now they look like this: <p>[img: <a
				# href="https://i.imgur.com/ABCDEF.jpg" rel="noopener noreferrer">data:image/gif;base64,R0lGODlhA</a>]</p>
				# But we want to get the link in the href attribute:
				try:
					for image in images:
						if image is None:
							print("NoneType, Skipping")
						else:
							image_link = image.a['href']
							print(f"[{item_file_name}] Image {images.index(image) + 1} "
							      f"(out of {len(images)}). Source: {image_link}")
							try:
								(
									image_content,
									image_extension,
									image_media_type
								) = get_image_from_url(
									url=image_link,
									image_format=default_image_format_config,
									compress_images=compress_images_config,
									max_image_size=max_image_size_config,
									debug=debug
								)
								images_downloaded[item.file_name][0] += 1
								image_path = f"images/" \
								             f"{item_file_name}_image_{images.index(image)}.{image_extension.lower()}"
								new_image = f"<img alt='Image {images.index(image)} from {item.file_name}' " \
								            f"style='text-align: center; margin: 2em auto; display: block;'" \
								            f" src='{image_path}' />"

								img = epub.EpubItem(
									uid=f"{item_file_name}_{images.index(image)}",
									file_name=image_path,
									media_type=image_media_type,
									content=image_content,
								)
								book.add_item(img)
								image.replace_with(BeautifulSoup(new_image, 'lxml-xml'))
							except Exception as e:
								print(f"Error with image {images.index(image) + 1}: {e}, skipping ...")
					item.content = (str(soup).encode('utf-8'))
				except Exception as e:
					print(f'Error while parsing images: {e}')
			except TypeError:
				print("NoneType error, skipping ...")

		try:
			total_number_of_images_downloaded = 0
			number_of_all_images_found = 0
			for _, chapter_image_list in images_downloaded.items():
				total_number_of_images_downloaded += chapter_image_list[0]
				number_of_all_images_found += chapter_image_list[1]

			if number_of_all_images_found != 0:
				try:
					epub_location = "/".join(path_to_epub.split("/")[:-1])
					epub.write_epub(f"{epub_location}/[FicImage]{file_name}.epub", book)
				except:
					epub.write_epub(f"[FicImage]{file_name}.epub", book)
				print(f'\nWrote [FicImage]{file_name}.epub')
				print(f"\nImage overview of {file_name}")
				print("=" * 54)
				for k, v in images_downloaded.items():
					print(f"{k}{' ' * (18 - len(k))}\t{v[0]} out of {v[1]} images downloaded")
				print("=" * 54)
				print(f"Total images downloaded: {total_number_of_images_downloaded}"
				      f" out of {number_of_all_images_found}")
				print("=" * 54)
			else:
				print("No images found. No new epub was created")

		except Exception as e:
			print(f'Error while writing epub: {e}')
	except FileNotFoundError:
		print(f'File {path_to_epub} not found.')
		return


def file_search(current_directory: str) -> list:
	files_path_list = []

	for dirpath, dirnames, files in os.walk(current_directory):
		for file in files:
			if file.endswith('.epub'):
				file_path = os.path.join(dirpath, file)
				files_path_list.append(file_path)

	if len(files_path_list) == 0:
		sys.exit("No epub files found!")

	print(f"Found {len(files_path_list)} files in total!")
	return files_path_list


def main() -> None:
	"""
	This function updates the FicHub epub file with images.
	:return: None
	"""

	parser = argparse.ArgumentParser(description="Update a FicHub epub file with images.")
	parser.add_argument("-p", "--path_to_epub", help="The path to the FicHub epub file.")
	parser.add_argument("-c", "--config_file_path", help="The path to the ficimage.json file.")
	parser.add_argument("-d", "--debug", help="Enable debug mode.", action="store_true")
	parser.add_argument(
		"-v",
		"--version",
		help="Prints out the current version and quits.",
		action='version',
		version=f"FicImage Version {__version__}"
	)
	parser.add_argument(
		"-r",
		"--recursive",
		help="This will update all files in the directory path given and its subdirectories.",
	)
	args = parser.parse_args()

	path_to_epub = args.path_to_epub
	config_file_path = args.config_file_path
	debug = args.debug
	recursive = args.recursive

	if path_to_epub is None and recursive is None:
		sys.exit("Either pass in a path to an epub or use the --recursive flag to convert the current directory and "
		         "its sub-directories")
	elif path_to_epub:
		if recursive:
			print("Ignoring --recursive flag since path_to_epub was given")
		update_epub(path_to_epub, config_file_path, debug)
	elif recursive:
		list_of_files = file_search(recursive)
		for i in list_of_files:
			try:
				update_epub(i, config_file_path, debug)
			except Exception as e:
				print(f"Error! Skipping {i}")
				if debug:
					print(f"Exception: {e}")


if __name__ == '__main__':
	main()

import setuptools

with open("PYPI_README.rst", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
	name="FicImageScript",
	version="2.1.0",
	author="Emmanuel C. Jemeni",
	author_email="jemenichinonso11@gmail.com",
	description="FicImage is an application designed to enhance the reading experience of FicHub epubs.",
	long_description=long_description,
	long_description_content_type="text/x-rst",
	url="https://github.com/Jemeni11/FicImage",
	project_urls={
		"Bug Tracker": "https://github.com/Jemeni11/FicImage/issues",
	},
	entry_points={
		'console_scripts': [
			'ficimage=FicImage.main:main'
		]
	},
	install_requires=[
		'beautifulsoup4==4.12.2',
		'certifi==2022.12.7',
		'charset-normalizer==3.1.0',
		'EbookLib==0.18',
		'idna==3.4',
		'lxml==4.9.2',
		'Pillow==9.5.0',
		'requests==2.29.0',
		'six==1.16.0',
		'soupsieve==2.4.1',
		'urllib3==1.26.15'
	],
	keywords="fanfiction fichub ficimage image download epub",
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Topic :: Internet :: WWW/HTTP",
	],
	packages=setuptools.find_packages('.'),
	python_requires=">=3.6"
)

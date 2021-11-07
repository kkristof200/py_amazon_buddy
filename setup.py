import setuptools, os

readme_path = os.path.join(os.getcwd(), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r") as f:
        long_description = f.read()
else:
    long_description = 'amazon_buddy'

setuptools.setup(
    name="amazon_buddy",
    version="2.0.29",
    author="Kristof",
    description="python wrapper for the amazon_buddy npm package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kkristof200/py_amazon_buddy",
    packages=setuptools.find_packages(),
    install_requires=[
        'beautifulsoup4>=4.10.0',
        'jsoncodable>=0.1.7',
        'kcu>=0.0.72',
        'ksimpleapi>=0.0.41',
        'noraise>=0.0.16',
        'requests>=2.26.0',
        'Unidecode>=1.3.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
import setuptools, os

readme_path = os.path.join(os.getcwd(), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r") as f:
        long_description = f.read()
else:
    long_description = 'amazon_buddy'

setuptools.setup(
    name="amazon_buddy",
    version="2.0.5",
    author="Kristof",
    description="python wrapper for the amazon_buddy npm package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kkristof200/py_amazon_buddy",
    packages=setuptools.find_packages(),
    install_requires=["ksimpleapi", "kcu", "requests", "jsoncodable", "Unidecode", "beautifulsoup4"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
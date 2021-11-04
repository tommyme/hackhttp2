import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hackhttp2",  # Replace with your own username
    version="0.0.2",
    author="ybw",
    author_email="2756456886@qq.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.baidu.com",
    # package_data={'hackhttp': ['*.md']},
    # package_dir={'hackhttp': 'hackhttp'},
    packages=setuptools.find_packages(),
    # include_package_data=True,
    python_requires='>=3.0',
)


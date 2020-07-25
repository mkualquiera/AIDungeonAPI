import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aidungeonapi", 
    version="0.0.2",
    author="1Macho",
    author_email="ozjuanpa@gmail.com",
    description="AI Dungeon api for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1Macho/AIDungeonAPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "gql>=v3.0.0a1"
    ]
)

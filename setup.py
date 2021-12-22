import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jackdaw-miicck",
    version="0.0.1",
    author="Michael Hutcheon (miicck)",
    author_email="michael.hutcheon@hotmail.co.uk",
    description="A digital audio workstation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miicck/jackdaw",
    project_urls={
        "Bug Tracker": "https://github.com/miicck/jackdaw/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)

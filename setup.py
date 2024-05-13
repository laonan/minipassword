import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="minipassword",
    version="1.0.0",
    author="Laonan",
    author_email="hello@laonan.net",
    description="Mini Password is a command-line password manager.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/laonan/minipassword",  # github url
    project_urls={
        "Bug Tracker": "https://github.com/laonan/minipassword/issues",
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    zip_safe=True,
    install_requires=[
        'simple-term-menu>=1.6.4',
        'cryptography>=42.0.7',
        'requests>=2.31.0',
    ],
    python_requires=">=3.6",
)

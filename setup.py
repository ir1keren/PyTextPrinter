from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pytextprinter",
    version="0.1.0",
    author="Irwan Darmawan",
    author_email="ir1keren@gmail.com",
    description="A Python library for advanced text printing utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ir1keren/pytextprinter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-socketio[asyncio]>=5.7.0",
        "aiohttp>=3.8.0",
        "websockets>=10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
        "hardware": [
            "pywin32>=227; sys_platform=='win32'",
        ],
        "websocket": [
            "python-socketio[asyncio]>=5.7.0",
            "aiohttp>=3.8.0", 
            "websockets>=10.0",
        ],
    },
)
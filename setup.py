#!/usr/bin/env python3
"""
Secure Sandbox - Python安全沙箱库

用于安全执行不可信的第三方代码（如AI生成的代码）
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="secure-sandbox",
    version="0.0.1",
    author="Python Security Architect",
    author_email="158119447@qq.com",
    description="高安全性Python沙箱库 - 用于安全执行不可信代码",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dotnet-7/secure-sandbox",
    project_urls={
        "Bug Tracker": "https://github.com/dotnet-7/secure-sandbox/issues",
        "Documentation": "https://github.com/dotnet-7/secure-sandbox/wiki",
        "Source Code": "https://github.com/dotnet-7/secure-sandbox",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        # 无外部依赖 - 纯Python实现
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
            "flake8>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "secure-sandbox=secure_sandbox.cli:main",
        ],
    },
    keywords=[
        "sandbox",
        "security",
        "code execution",
        "AI code",
        "unsafe code",
        "restricted execution",
        "gas mechanism",
        "AST whitelist",
    ],
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)
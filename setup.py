"""Setup script for model-cost-advisor."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="model-cost-advisor",
    version="1.2.0",
    author="minirr890112-byte",
    author_email="minirr890112-byte@users.noreply.github.com",
    description="Analyze any task and recommend the most cost-effective LLM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/minirr890112-byte/model-cost-advisor",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(include=["model_cost_advisor", "model_cost_advisor.*"]),
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "model-cost=model_cost_advisor.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="llm, ai, cost, pricing, openai, claude, deepseek, gemini, optimization",
    project_urls={
        "Bug Reports": "https://github.com/minirr890112-byte/model-cost-advisor/issues",
        "Source": "https://github.com/minirr890112-byte/model-cost-advisor",
    },
)

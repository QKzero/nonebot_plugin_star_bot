from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = "nonebot-plugin-star-bot",
    version = "1.1.2",
    author = "QKzero",
    description = "A plugin based on NoneBot2 and personal used.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/QKzero/nonebot_plugin_star_bot",
    project_urls={
        "Bug Tracker": "https://github.com/QKzero/nonebot_plugin_star_bot",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=["nonebot_plugin_star_bot"],
    python_requires=">=3.7",
    install_requires=[
        "nonebot2 >= 2.0.0b2",
        "nonebot-adapter-onebot >= 2.0.0b1"
    ]
)
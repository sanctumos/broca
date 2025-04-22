from setuptools import setup, find_packages

setup(
    name="broca2",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "telethon",
        "python-dotenv",
        "sqlalchemy",
        "aiosqlite",
    ],
) 
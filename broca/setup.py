from setuptools import setup, find_packages

setup(
    name="broca-core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiosqlite>=0.19.0",
        "flask>=2.3.3",
        "letta_client>=0.1.123",
        "python-dateutil>=2.8.2",
        "python-dotenv>=1.0.0",
        "telethon>=1.28.5",
        "typing-extensions>=4.7.1",
    ],
) 
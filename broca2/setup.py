from setuptools import setup, find_packages

setup(
    name="broca2",
    version="0.9.0",
    packages=find_packages(),
    install_requires=[
        "telethon",
        "python-dotenv",
        "sqlalchemy",
        "aiohttp",
        "emoji",
        "rich",
        "typer",
        "pydantic",
        "markdown"
    ],
    entry_points={
        "console_scripts": [
            "broca2=main:main",
            "broca-admin=cli.broca_admin:main"
        ]
    }
) 
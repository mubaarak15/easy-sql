from setuptools import setup, find_packages

setup(
    name="easy-sql",  
    version="0.4.0", 
    description="A Python package for simplified database interactions with SQLite and MySQL.",
    long_description=open("README.md", "r", encoding="utf-8").read(),  
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/easy-sql",  
    author="Mubaarak Abdikadir Jamac", 
    author_email="Mubaaraksboy@gmail.com",  
    packages=find_packages(),
    install_requires=[
        "mysql-connector-python==9.1.0",
        "SQLAlchemy==2.0.36"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
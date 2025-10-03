from setuptools import setup, find_packages

setup(
    name="running-recsys",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.118.0",
        "uvicorn>=0.37.0",
        "httpx>=0.28.1",
        "osmnx>=2.0.6",
        "networkx>=3.5",
        "shapely>=2.1.2",
        "polyline>=2.0.3",
        "pydantic>=2.11.9",
        "python-dotenv>=1.1.1",
        "folium",
    ],
    python_requires=">=3.10",
)

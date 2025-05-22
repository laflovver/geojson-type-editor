from setuptools import setup, find_packages

setup(
    name="geojson-editor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "PySide6>=6.4.0",
        "requests>=2.28.0",
        "jsonschema>=4.17.0",
    ],
    extras_require={
        "dev": [
            "black>=22.12.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pytest>=7.2.0",
            "pytest-cov>=4.0.0",
            "types-requests>=2.28.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "geojson-editor=geojson_editor.main:main",
        ],
    },
)

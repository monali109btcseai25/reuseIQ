from setuptools import setup, find_packages

setup(
    name="reuseiq",
    version="1.0.0",
    description="ReUseIQ: Intelligent E-Waste Reuse and Recycling Advisor",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "rdflib>=7.0.0",
        "pandas",
        "plotly",
        "streamlit",
        "pytest"
    ],
)

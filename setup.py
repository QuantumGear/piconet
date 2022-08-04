from setuptools import setup, find_namespace_packages

with open("requirements.txt") as f:
    install_reqs = f.read().strip().split("\n")

# Filter out comments/hashes from requirements.txt
reqs = []
for req in install_reqs:
    if req.startswith("#") or req.startswith("    --hash="):
        continue
    reqs.append(str(req).rstrip(" \\"))

setup(
    name="piconet",
    version="0.0.1",
    license="MIT license",
    url="https://github.com/quantumgear/piconet",
    description="RPC server and command line tool for picoscopes",
    author="Stepan Snigirev, Jan Trautmann",
    author_email="snigirev.stepan@gmail.com",
    packages=find_namespace_packages("src", include=["*"]),
    package_dir={"": "src"},
    install_requires=reqs,
    entry_points={
        "console_scripts": [
            "piconet-cli=piconet.cli:main",
            "piconetd=piconet.server:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

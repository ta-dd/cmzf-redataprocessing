from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'A download of real estate offers from Sreality.cz'

setup(
    name="redataprocessing",
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.txt").read(),
    author="Vojtěch Kania, Lukáš Novotný",
    author_email="vojtech.kania@gmail.com, 30702889@fsv.cuni.cz",
    license='MIT',
    packages=find_packages(),
    install_requires=["python-certifi-win32"],
    keywords='real estate',
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
    ]
)
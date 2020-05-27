from setuptools import setup, find_packages

setup(
    name='sclang',
    version='0.1',
    author='Alexis Boisserand',
    author_email='alexis.boisserand@gmail.com',
    packages=find_packages(exclude=['tests']),
    license='MIT',
    description='declarative language for statecharts',
    long_description='sclang is a compact declarative language for describing statecharts.',
    url='https://github.com/alexis-boisserand/sclang',
    install_requires=[
        'cached-property>=1.5',
        'lark-parser>=0.8',
        'Jinja2>=2.11'
    ],
    extras_require={
        'dev': [
            'pytest>=5.3.5'
        ]
    },
    python_requires='>=3.5',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    include_package_data=True
)

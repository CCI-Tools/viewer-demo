from setuptools import setup

setup(
    name="ccitbxws",
    version="0.0.1",
    description='CCI Toolbox Server',
    license='GPL 3',
    author='Brockmann COnsult GmbH',
    packages=['ccitbxws'],
    entry_points={
        'console_scripts': [
            'ccitbxws = ccitbxws.main:main',
        ]
    },
    install_requires=['h5py >= 2.5',
                      'numpy >= 1.7',
                      'matplotlib >= 1.5',
                      'Pillow >= 3.1',
                      'falcon >= 0.3',
                      'CherryPy >= 3.8'],
)

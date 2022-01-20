from distutils.core import setup

setup(
    name='vacdec',
    version='',
    packages=[''],
    url='',
    license='',
    author='Hanno Böck',
    author_email='',
    description='',
    python_requires='>=3.7, <4',
    install_requires=['requests', 'base45', 'cbor2', 'pillow', 'pyzbar', 'cose', 'cryptojwt', 'pyasn1', 'pycountry'],
    scripts=['vacdec'],
)

from setuptools import setup, find_packages


setup(
    name="sweetns",
    version=__import__('sweetns').__version__,
    url='http://github.com/stefanfoulis/sweetns',
    license='BSD',
    platforms=['OS Independent'],
    description="A redis powered DNS server and forwarder built on Twisted.",
    author='Stefan Foulis',
    author_email='stefan@foulis.ch',
    packages=find_packages(),
    install_requires=[
        'Twisted',
        'txredisapi',
        'click',
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points='''
        [console_scripts]
        sweetns=sweetns.cli:main
    ''',
)

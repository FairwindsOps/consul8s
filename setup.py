"""
Consul integration with Kubernetes
"""
from setuptools import find_packages, setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='consul8s',
    version='0.0.0',
    url='https://github.com/FairwindsOps/consul8s',
    license='Apache2',
    author='Philip Cristiano',
    author_email='philip@fairwinds.com',
    description='Consul integration with Kubernetes',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'consul8s = consul8s.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

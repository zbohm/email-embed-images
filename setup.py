from setuptools import find_packages, setup

setup(
    author='Zdeněk Böhm',
    author_email='zdenek.bohm@seznam.cz',
    name='email-embed-images',
    version='1.0.0',
    description='Embed linked images to email.',
    url='https://github.com/zbohm/email-embed-images',
    license='BSD 3-Clause License',
    platforms=['OS Independent'],
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ),
    install_requires=(
        'lxml',
        'requests',
    ),
    extras_require={
        'quality': ['isort', 'flake8', 'pydocstyle', 'mypy'],
        'test': ['pyfakefs', 'requests_mock', 'tox']
    },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

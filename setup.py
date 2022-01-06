from setuptools import setup

exec(open('sa_dbmgt/version.py').read())

setup(
    name='sa-dbmgt',
    version=__version__,
    description='Database management library',
    author='xiema',
    author_email='maxprincipe@yahoo.com',
    url='http://www.github.com/xiema',
    license='Unlicense',
    packages=['sa_dbmgt'],
    install_requires=['sqlalchemy',],

    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)


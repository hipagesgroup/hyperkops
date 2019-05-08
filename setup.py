from setuptools import setup

setup(
    name='hyperkops',
    version='0.1',
    description='Monitoring tool which enables running hyperopt in kubenetes',
    url='https://github.com/hipagesgroup/hyperkops',
    author='hipages Datascience',
    packages=['hyperkops'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'hyperkops-monitor=hyperkops.monitor:main_monitor'
        ]},
    install_requires=[
        'hyperopt==0.1.2',
        'dill==0.2.9',
        'pymongo==3.8.0',
        'python-dateutil==2.8.0']
)

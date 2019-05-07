from setuptools import setup, find_packages

setup(
    name='hyperkops',
    version='0.1',
    description='Monitoring tool which enables running hyperopt in kubenetes',
    url='https://github.com/hipagesgroup/hyperkops',
    author='hipages Datascience',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'hyperkops-monitor=hyperkops.monitor.hyperopt_monitor:main_monitor',
        ]},
    install_requires=[
        'hyperopt==0.1.2',
        'pymongo==3.8.0',
        'python-dateutil==2.8.0']
)

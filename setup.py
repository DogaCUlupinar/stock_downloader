from setuptools import setup

setup(name="stock_downloader",
      version="0.0.1",
      author="Doga Ulupinar",
      author_email="doga.supplementary@gmail.com",
      license="MIT",
      packages=["stock_download"],
      entry_points={
          'console_scripts':[
              'downloader=stock_download.downloader:main'
          ]
      },
      install_requires=['numpy==1.11.1',
                        'pandas==0.18.1',
                        'pandas-datareader==0.2.1',
                        'python-dateutil==2.5.3',
                        'pytz==2016.6.1',
                        'requests==2.11.1',
                        'requests-file==1.4',
                        'six==1.10.0'])




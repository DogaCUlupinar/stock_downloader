## INSTALLATION INSTRUCTIONS ##
Hi babacim. All you should have to do is the following
You have two option. install using pip (which should be easier) and isntall using conda. you will need git installed for pip

### USING PIP ###
Fast way using git:
just type this:

pip install --upgrade --no-deps --force-reinstall  git+https://github.com/DogaCUlupinar/stock_downloader@master

OR if you want the source code your current directory

pip install -e git+https://github.com/DogaCUlupinar/stock_downloader.git@master#egg=stock_downloader

Slow way using tarball:
download the source code
>>python setup.py install

### USING CONDA ###
you will need to first clone the repo
then on the top level you will need to run:
>>conda build stock_download
>>conda install --use-local stock_downloader

## USING THE CODE ##
the code will automagically put an executable script in the appropriate bin directory. so all you will have to do is just call ./downloader <output_dir>


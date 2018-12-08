from setuptools import setup
setup(name='sqlupgrade',
      version='1.0',
      py_modules=['sqlupgrade'],
      install_requires=['PyMySQL'],
      scripts=['sqlupgrade.py']
          
      )

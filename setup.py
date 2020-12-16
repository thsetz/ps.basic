from setuptools import setup 
import os



version = '1.2.6'

INSTALL_REQUIRES=[ 'setuptools', 'docopt' ,'pygraphviz'  ]

setup(name='ps.basic',
      version=version,
      description="Basic class used in PS environment",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("CHANGES.txt")).read(),
      classifiers=[
          #'Development Status :: 5 - Stable',
          'Environment :: Console',
          #'Intended Audience :: DevOps',
          'License :: Other/Proprietary License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.9 :: ',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Utilities'
      ],
      keywords='PS',
      author='Setz',
      author_email='thomas@setz.de',
      url='https://bitbucket.org/drsetz/ps.basic',
      license='GPL',
      packages=['ps.basic'],
      package_dir={'': 'src'},
      #include_package_data=True,
      zip_safe=False,
      install_requires=INSTALL_REQUIRES ,
      entry_points={
          'console_scripts': [
              'ps_shell_log=ps.ps_shell_log:main',
          ],
      },

      )

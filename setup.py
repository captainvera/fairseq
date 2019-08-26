#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import setup, find_packages, Extension
import sys


if sys.version_info < (3,):
    sys.exit('Sorry, Python3 is required for fairseq.')

with open('README.md') as f:
    readme = f.read()

if sys.platform == 'darwin':
    extra_compile_args = ['-stdlib=libc++']
else:
    extra_compile_args = ['-std=c++11']
bleu = Extension(
    'fairseq.libbleu',
    sources=[
        'fairseq/clib/libbleu/libbleu.cpp',
        'fairseq/clib/libbleu/module.cpp',
    ],
    extra_compile_args=extra_compile_args,
)


def get_cython_modules():
    token_block_utils = Extension(
        "fairseq.data.token_block_utils_fast",
        ["fairseq/data/token_block_utils_fast.pyx"],
    )
    data_utils_fast = Extension(
        "fairseq.data.data_utils_fast",
        ["fairseq/data/data_utils_fast.pyx"],
        language="c++",
    )
    return [token_block_utils, data_utils_fast]


def my_build_ext(pars):
    """
    Hack to import numpy headers for cython without assuming numpy is
    pre-installed on the system.
    More details: https://stackoverflow.com/questions/54117786/add-numpy-get-include-argument-to-setuptools-without-preinstalled-numpy
    """
    # import delayed:
    from setuptools.command.build_ext import build_ext as _build_ext

    # include_dirs adjusted:
    class build_ext(_build_ext):
        def finalize_options(self):
            _build_ext.finalize_options(self)
            # Prevent numpy from thinking it is still in its setup process:
            __builtins__.__NUMPY_SETUP__ = False
            import numpy
            self.include_dirs.append(numpy.get_include())
    # Object returned:
    return build_ext(pars)


setup(
    name='fairseq',
    version='0.8.0',
    description='Facebook AI Research Sequence-to-Sequence Toolkit',
    url='https://github.com/pytorch/fairseq',
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    long_description=readme,
    long_description_content_type='text/markdown',
    setup_requires=[
        'numpy',
        'cython',
        'setuptools>=18.0',
    ],
    install_requires=[
        'cffi',
        'fastBPE',
        'numpy',
        'regex',
        'sacrebleu',
        'torch',
        'tqdm',
    ],
    packages=find_packages(exclude=['scripts', 'tests']),
    ext_modules=get_cython_modules() + [bleu],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'fairseq-eval-lm = fairseq_cli.eval_lm:cli_main',
            'fairseq-generate = fairseq_cli.generate:cli_main',
            'fairseq-interactive = fairseq_cli.interactive:cli_main',
            'fairseq-preprocess = fairseq_cli.preprocess:cli_main',
            'fairseq-score = fairseq_cli.score:main',
            'fairseq-train = fairseq_cli.train:cli_main',
            'fairseq-validate = fairseq_cli.validate:cli_main',
        ],
    },
    cmdclass={'build_ext': my_build_ext},
    zip_safe=False,
)

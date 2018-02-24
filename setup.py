import setuptools
from pub2sd.myclasses.myconst.therest import THIS_VERSION

setuptools.setup(
    name="pub2sd",
    version=THIS_VERSION,
    url="https://github.com/madskinner/pub2sd2",
    author="Mark Skinner",
    author_email="mark_skinner@sil.org",
    description="Publish MP3 files to SD cards",
    long_description=open('README.rst').read(),
#    data_files=[('../tests', ['set_tags.json', 'default_values.json', 'hash_tag_on.json', 'idiot_tags.json', 'localized_text.json', 'read_tag.json', 'read_tag_hide_encoding.json', 'read_tag_info.json', 'trim_tag.json',]),]
#                ('', ['set_tags.json', 'default_values.json', 'hash_tag_on.json', 'idiot_tags.json', 'localized_text.json', 'read_tag.json', 'read_tag_hide_encoding.json', 'read_tag_info.json', 'trim_tag.json',]),],
    packages=setuptools.find_packages(),
#    package_data={'pub2sd': ['*.html', '*.json', '*.ico', 'images/*.png', 'images/*.jpg', 'images/*.ico']},
    package_data={'pub2sd': ['*.html', '*.ico', 'images/*.png', 'images/*.jpg', 'images/*.ico']},
    install_requires=["lxml","psutil","mutagen","unidecode"],
    license='MIT',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6'],
    keywords='publish mp3 metadata sdcard',
    include_package_data=True
)

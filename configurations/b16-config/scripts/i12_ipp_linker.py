import os
from os.path import join

def create_links(path):
    file_names = os.listdir(path)
    file_names.sort()
    file_numbers = [int(f.split('.TIF')[0].split('ipp')[1]) for f in file_names]
    link_names = ['p_%05d.tif' % n for n in file_numbers]

    os.mkdir(join(path, 'links'))
    for file_name, link_name in zip(file_names, link_names):
        src = join('..', file_name)
        dst = join(path, 'links', link_name)
        print dst, "->", src
        os.symlink(src, dst)

   

# /scratch/2013-3-20

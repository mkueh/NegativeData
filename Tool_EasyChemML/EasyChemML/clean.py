import glob, os, sys, shutil

pathfile = os.path.dirname( __file__ )
print('delete all created files')

files = [os.path.abspath(f) for f in glob.glob('./Output/**', recursive=True)]

for f in files:
    print(f)
    if not os.path.isdir(f):
        os.remove(f)
        pass

print('remove ZARR_TMP')
if os.path.exists('./ZARR_TMP'):
    shutil.rmtree('./ZARR_TMP')

files = [os.path.abspath(f) for f in glob.glob('./output.*', recursive=True)]

for f in files:
    print(f)
    if not os.path.isdir(f):
        os.remove(f)
    pass
import os
import glob

folds = glob.glob('./Los/U10/*')

print(folds)
for f in folds:
    files = glob.glob('/%s/*.xlsx' %f)
    print(files)
    for fi in files:
        for i in range(1, 1):
            os.startfile(fi, 'print')
        print(fi)
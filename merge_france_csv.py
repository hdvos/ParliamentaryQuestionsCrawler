from csv import DictReader, DictWriter
import os
from tqdm import tqdm

filelist = os.listdir("csv_files")
filelist = [os.path.join("csv_files", filenm) for filenm in filelist]

with open(filelist[0], 'rt') as f:
    reader = DictReader(f, delimiter='\t')
    firstline = reader.__next__()
    fieldnames = list(firstline.keys())

filedict = {int(filenm.replace(".csv", "").replace("csv_files/","")):filenm for filenm in filelist}

with open("france_merged_half.csv", 'wt') as out:
    writer = DictWriter(out, delimiter = '\t', fieldnames = fieldnames)
    writer.writeheader()
    for _, filename in tqdm(sorted(filedict.items(), key = lambda x:x[0]), total=len(filelist)):
        with open(filename, 'rt') as f:
            reader = DictReader(f, delimiter = "\t")
            for row in reader:
                writer.writerow(row)


print("done")
import os,sys,pdb
import cv2
import argparse
import numpy as np
import multiprocessing as mp
import random
def run_one_class(args):
    indir,outdir,totalAfterCrop,cropWR,cropHR,flagResize = args
    jpgs = os.listdir(indir)
    total = np.int64((totalAfterCrop - len(jpgs)) / len(jpgs))
    if total < 1:
        return

    try:
        os.makedirs(outdir)
    except Exception,e:
        pass

    for jpg in jpgs:
        sname,ext = os.path.splitext(jpg)
        if '.jpg' != ext:
            continue
        img = cv2.imread(os.path.join(indir,jpg),1)
        cropW = np.int64(img.shape[1] * cropWR)
        cropH = np.int64(img.shape[0] * cropHR)
        accessSet= set([])
        trynum = 0
        while 1:
            if len(accessSet) >= total:
                break
            x = random.randint( 0, img.shape[1] - 1 - cropW)
            y = random.randint( 0, img.shape[0] - 1 - cropH)
            mark = '%d_%d'%(x,y)
            if mark in accessSet:
                trynum += 1
                if trynum > 100:
                    break
                continue
            trynum -= 1
            if trynum < 0:
                trynum = 0
            accessSet.add(mark)
            if flagResize != 0:
                cropImg = cv2.resize( img[y:y+cropH,x:x+cropW,:], (img.shape[1],img.shape[0]))
            else:
                cropImg = img[y:y+cropH,x:x+cropW,:]
            cv2.imwrite( os.path.join(outdir, sname + ",crop%d_%d_%d_%d.jpg"%(x,y,cropW,cropH)),cropImg)
    return

def run(indir,outdir,cropW,cropH,numPerClass,cpu,flagResize):
    params = []
    objs = os.listdir(indir)
    for obj in objs:
        fname = os.path.join(indir, obj)
        if not os.path.isdir(fname):
            continue
        params.append( (fname, os.path.join(outdir,obj), numPerClass,cropW,cropH, flagResize) )
    pool = mp.Pool(cpu)
    pool.map(run_one_class, params)
    pool.close()
    pool.join()
    return

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('indir',help='input dir')
    ap.add_argument('outdir',help='output dir')
    ap.add_argument('-numPerClass',help='sample number of each classes after crop',default=400, type=np.int64) # set it to double of maximum number
    ap.add_argument('-cropW',help='cropped width wrt origin image [0,1]',default=0.9, type=np.float64)
    ap.add_argument('-cropH',help='cropped height wrt origin image [0,1]',default=0.9, type=np.float64)
    ap.add_argument('-resize',help='resize after crop to keep size unchanged', default=1, type=np.int64)
    ap.add_argument('-cpu',help='thread number',default=2, type=np.int64)
    args = ap.parse_args()
    run(args.indir, args.outdir, args.cropW, args.cropH, args.numPerClass, args.cpu, args.resize)

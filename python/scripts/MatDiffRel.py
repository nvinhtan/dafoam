#!/usr/bin/env python
'''
Compare values in two different matrices
and identify the max relative error
Example:
python MatDiffRel.py dRdWT1.bin dRdWT2.bin
'''
import os,sys
import argparse
import petsc4py
petsc4py.init(sys.argv)
from petsc4py import PETSc

def evalMatDiffRel(mat1,mat2,diffTol=1e-16):
    # the relative error is computed as
    # (mat1-mat2)/mat1

    # read  mat 1
    jacMat1 = PETSc.Mat().create(PETSc.COMM_WORLD)
    viewer = PETSc.Viewer().createBinary(mat1,comm=PETSc.COMM_WORLD)
    jacMat1.load(viewer)
    
    # read  mat 2
    jacMat2 = PETSc.Mat().create(PETSc.COMM_WORLD)
    viewer = PETSc.Viewer().createBinary(mat2,comm=PETSc.COMM_WORLD)
    jacMat2.load(viewer)
    
    Istart,Iend = jacMat1.getOwnershipRange()
    
    # absolute error
    jacMatDiff = PETSc.Mat().create(PETSc.COMM_WORLD)
    viewer = PETSc.Viewer().createBinary(mat1,comm=PETSc.COMM_WORLD)
    jacMatDiff.load(viewer)
    jacMatDiff.axpy(-1.0,jacMat2,structure=jacMatDiff.Structure.DIFFERENT_NONZERO_PATTERN)
    
    maxDiff = -1.0e12
    maxVal1 = -1.0e12
    maxVal2 = -1.0e12
    maxRowI = -1.0e12
    maxColI = -1.0e12
    l2norm=0.0
    foundDiff=0
    for i in xrange(Istart, Iend):
        rowVals = jacMatDiff.getRow(i)
        nCols = len(rowVals[0])
        for j in range(nCols):
            colI=rowVals[0][j]
            valDiff=abs(rowVals[1][j])
            valRef = abs(jacMat1[i,colI])
            valRelError = valDiff/(valRef+diffTol)
            l2norm = l2norm + valRelError**2
            if valRelError>diffTol:
                if valRelError>maxDiff:
                    foundDiff=1
                    maxDiff=valRelError
                    maxRowI=i
                    maxColI=colI
                    maxVal1 = jacMat1.getValue(i, colI)
                    maxVal2 = jacMat2.getValue(i, colI)
    l2norm = l2norm**0.5
    
    if foundDiff==1:
        print('L2Norm: %20.16e'%l2norm)
        print('MaxDRel: %20.16e' %maxDiff)
        print('MaxVal1: %20.16e' %maxVal1)
        print('MaxVal2: %20.16e' %maxVal2)
        print('MaxrowI: %d' %maxRowI)
        print('MaxcolI: %d' %maxColI)
        return maxDiff
    else:
        print('Two matrices are exactly same with tolerance: %e'%diffTol)
        return 0.0,0.0

if __name__ == '__main__':
    print("\nUsage: python MatDiffRel.py matName1 matName2")
    print("Example python MatDiffRel.py dRdWT1.bin dRdWT2.bin\n")
    evalMatDiffRel(sys.argv[1],sys.argv[2])

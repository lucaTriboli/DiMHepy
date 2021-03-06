#!/usr/bin/python3
import sys
import matplotlib
if(sys.argv.count('-d')==0):
    matplotlib.use('Agg')
import subprocess
import numpy as NP
from matplotlib import pyplot as PLT
import seaborn as sns
import pandas as pd
import scipy.spatial as sp
from scipy.cluster.hierarchy import dendrogram
import scipy.cluster.hierarchy as hc
from PIL import Image                                                                                
from matplotlib.colors import LinearSegmentedColormap
sns.set(color_codes=True)
import matplotlib.lines as mlines
import tkinter.messagebox

###########################################################################################################
#Functions
 
#Function that read matrices from file, create percentageIdentityMatrix with percentage_identity matrix values,
#alignmentLengthsMatrix with alignment_length matrix values and
#nameList with samples names
def MatrixFromFile(NameFile):
    percentageIdentityMatrix=[]
    nameList=[]
    file = open(NameFile)
    for line in file.readlines():
        if len(nameList)==0:
            nameList=[ x for x in (line.split('\t'))[1:] ]
            nameList[-1] = nameList[-1][:-1]
        else:
            percentageIdentityMatrix += [[ float(x) for x in (line.split('\t'))[1:] ]]
    return percentageIdentityMatrix, nameList
    

def onclick(event):
    if 151<event.y<640:
        if 177<event.x<670:
            dfmClicked=dataFrameMatrix1
            dfmOther=dataFrameMatrix2
        elif 770<event.x<1260:
            dfmClicked=dataFrameMatrix2
            dfmOther=dataFrameMatrix1
        x = int(NP.round(event.xdata))
        y = int(NP.round(event.ydata))
        g1 = float("{0:.2f}".format(dfmClicked[y, x]))
        g2 = float("{0:.2f}".format(dfmOther[x, y]))
        testo=('First Species: '+'\n'+str(nameList[LowerNewIndexOrder[y]])+'\n'+'Second Species: '+'\n'+ \
                                        str(nameList[LowerNewIndexOrder[x]])+'\n'+'ANI value: '+'\n'+str(g1)+'\n'+'Alignment value: '+'\n'+str(g2))
        if dfmClicked[y, x]!=0 or dfmOther[y, x]!=0:
            print('ANI value: ', g1)
            print('Alignment value: ', g2)
            print('First Species: ', nameList[LowerNewIndexOrder[y]])
            print('Second Species: ', nameList[LowerNewIndexOrder[x]])
            print('----------------------------------------------------------------------------')
            tkinter.messagebox.showinfo("Title",testo)
    
#############################################################################################################
#Now I can read command line parameters, save them in parameterList, then create 2 matrices and the samples list 


parameterList = sys.argv[1:]
if (parameterList.count('-i')==1 and parameterList.count('-o')==1) or (parameterList.count('-ip')==1 and parameterList.count('-ia')==1) and parameterList.count('-oss')==1:
    if (parameterList.count('-i')==1 and parameterList.count('-o')==1):
        indexInput=parameterList.index('-i')
        outputFolderIndex=parameterList.index('-o')
        print("pyani is working, please wait")
        subprocess.call(['python3', '/home/luca/pyani/pyani/bin/average_nucleotide_identity.py', '-i', parameterList[indexInput+1], '-o', parameterList[outputFolderIndex+1]])
        print("pyani has finished, now SoftStar is working")
        percentageIdentityFileName = (parameterList[outputFolderIndex+1]+'/ANIm_percentage_identity.tab')
        alignmentLenghtsFileName = (parameterList[outputFolderIndex+1]+'/ANIm_alignment_lengths.tab')
    else:
        indexInputPerceFile=parameterList.index('-ip')
        indexInputAlignFile=parameterList.index('-ia')
        percentageIdentityFileName = (parameterList[indexInputPerceFile+1])
        alignmentLenghtsFileName = (parameterList[indexInputAlignFile+1])
    
    outputPNGIndex=parameterList.index('-oss')
    outputName = parameterList[outputPNGIndex+1]
    
    percentageIdentityMatrix, nameList = MatrixFromFile(percentageIdentityFileName)
    alignmentLengthsMatrix, nameList2 = MatrixFromFile(alignmentLenghtsFileName)
    alignmentLengthsMatrix = NP.log10(alignmentLengthsMatrix)
    NUMERO_CAMPIONI=len(nameList)
    
    print('Meanwhile, the number of genomes you put in is:', NUMERO_CAMPIONI)
    
    #############################################################################################################
    #Build the upper and lower half matrix and reorder based on lower half
    dataFrameMatrix1 = pd.DataFrame(percentageIdentityMatrix)
    dataFrameMatrix2 = pd.DataFrame(alignmentLengthsMatrix)


    #I find the new order for lower half heatmap
    dataFrameMatrix1_corr = dataFrameMatrix1.T.corr()
    dataFrameMatrix1_dism = 1 - dataFrameMatrix1_corr
    linkage = hc.linkage(sp.distance.squareform(dataFrameMatrix1_dism), method='ward')
    gLower=sns.clustermap(dataFrameMatrix1_dism, row_linkage=linkage, col_linkage=linkage)
    PLT.close()
    LowerNewIndexOrder = gLower.dendrogram_row.reordered_ind

    #I find the new order for upper half heatmap
    dataFrameMatrix2_corr = dataFrameMatrix2.T.corr()
    dataFrameMatrix2_dism = 1 - dataFrameMatrix2_corr
    linkage2 = hc.linkage(sp.distance.squareform(dataFrameMatrix2_dism), method='ward')
    
    #I create matrices to mask the upper half for the first matrix and the lower half for the second one
    maskMatrix1 = NP.triu(dataFrameMatrix1, k=1)
    dataFrameMatrix1mask = NP.ma.masked_where(maskMatrix1, dataFrameMatrix1)


    maskMatrix2 = NP.tril(dataFrameMatrix2, k=-1)
    dataFrameMatrix2 = NP.ma.masked_where(maskMatrix2, dataFrameMatrix2)


    #I reorder matrices data based on lower half order
    for i in range(NUMERO_CAMPIONI):
        for j in range(NUMERO_CAMPIONI):
            if i<j:
                dataFrameMatrix2[i, j]=alignmentLengthsMatrix[LowerNewIndexOrder[i]][LowerNewIndexOrder[j]]
            if i>j:
                dataFrameMatrix1mask[i, j]=percentageIdentityMatrix[LowerNewIndexOrder[i]][LowerNewIndexOrder[j]]

    #############################################################################################################
    #I prepare output window (firstSlot for upper matrix, thirdSlot for lower matrix and secondSlot for text)

    if NUMERO_CAMPIONI<=30:
        imgSize = (14, 8)
    elif NUMERO_CAMPIONI<=100:
        imgSize = (21, 12)
    else:
        imgSize = (28, 16)

    outputWindow = PLT.figure(num = 'Output Window', figsize = imgSize)
    firstSlot = outputWindow.add_subplot(1, 2, 1)
    thirdSlot = outputWindow.add_subplot(1, 2, 2)
    
    cid = outputWindow.canvas.mpl_connect('button_press_event', onclick)

    #I write strings in output window
    iniziosx=0.125+0.35/NUMERO_CAMPIONI
    scalinoup=0.3/NUMERO_CAMPIONI
    scalinodx=0.35/NUMERO_CAMPIONI
    stepdx=scalinodx
    inizioup=0.8-scalinoup
    lineafissa=inizioup
    finedx=0.525
    puntomedio=iniziosx+(finedx-iniziosx)/2.0
    
    if NUMERO_CAMPIONI<40:
        fontSize = 13
    elif NUMERO_CAMPIONI<=100:
        fontSize = 8
    else:
        fontSize = 7
    
    
    for i in range(NUMERO_CAMPIONI):
        testo=nameList[LowerNewIndexOrder[i]]
        if i%2==1:
            l1 = mlines.Line2D([0.125+scalinodx+0.01, puntomedio+(puntomedio-0.105-scalinodx)], [lineafissa, lineafissa], transform=outputWindow.transFigure, figure=outputWindow, color='lightgrey', lw='2')
            outputWindow.lines.extend([l1])
            secondSlot = outputWindow.text(puntomedio-(len(testo)/2)*0.006, inizioup, testo, size=fontSize, backgroundcolor='lightgrey', style='italic')
            
        secondSlot = outputWindow.text(puntomedio-(len(testo)/2)*0.006, inizioup, testo, size=fontSize, style='italic')
        puntomedio+=(0.35/NUMERO_CAMPIONI)
        inizioup-=(0.6/(NUMERO_CAMPIONI-0.5))
        lineafissa-=(0.6/(NUMERO_CAMPIONI-0.25))
        scalinodx+=stepdx
    
    
    ##############################################################################################
    #show output from 2 distance matrices below and under the text (samples names) and adjust colorbars and colormaps

    vmax = 4.0
    cmap = LinearSegmentedColormap.from_list('mycmap', [(0 / vmax, 'blue'),
                                                        (1 / vmax, 'lightBlue'),
                                                        (2 / vmax, 'white'), 
                                                        (3 / vmax, '#eeac1e'),
                                                        (4 / vmax, 'red')]
                                            )

    colorBarLowerAxes = outputWindow.add_axes([0.04, 0.5, 0.01, 0.3])
    colorBarUpperAxes = outputWindow.add_axes([0.92, 0.5, 0.01, 0.3])
    if(parameterList.count('-ignDiag')==1):
        tmpDFM1=dataFrameMatrix1
        for i in range(0,len(tmpDFM1)):
            tmpDFM1[i][i]=sum(tmpDFM1[i])/len(tmpDFM1[i])
        tmpDFM1mask = NP.ma.masked_where(maskMatrix1, tmpDFM1)
        lowerMat = firstSlot.imshow(tmpDFM1mask, interpolation="nearest", cmap=cmap)
    else:
        lowerMat = firstSlot.imshow(dataFrameMatrix1mask, interpolation="nearest", cmap=cmap)

    upperMat = thirdSlot.imshow(dataFrameMatrix2, interpolation="nearest", cmap=cmap)
    
    cbarLower = outputWindow.colorbar(lowerMat, cax=colorBarLowerAxes)
    cbarLower.ax.set_title('A.N.I.')
    cbarUpper = outputWindow.colorbar(upperMat, cax=colorBarUpperAxes)
    cbarUpper.set_label('Alignment length (log10)')

    dendrogramLowerAxes = outputWindow.add_axes([0.125, 0.050625, 0.355, 0.135])
    dendrogram(linkage,  orientation='bottom')
    dendrogramUpperAxes = outputWindow.add_axes([0.545, 0.805, 0.355, 0.15])
    dendrogram(linkage)

    dendrogramLowerAxes.grid(False)
    dendrogramLowerAxes.set(frame_on=False, xticks=[], yticks=[])
    dendrogramUpperAxes.grid(False)
    dendrogramUpperAxes.set(frame_on=False, xticks=[], yticks=[])


    firstSlot.set(frame_on=False, aspect=1, xticks=[], yticks=[])
    thirdSlot.set(frame_on=False, aspect=1, xticks=[], yticks=[])


    firstSlot.grid(False)
    thirdSlot.grid(False)


    ##############################################################################################
    #print output
    print("All operations have been finished, here is your output:", outputName)
    PLT.savefig(outputName)
    if(parameterList.count('-s')==1):
        img = Image.open(outputName)
        img.show() 

    PLT.show()
    
elif (parameterList.count('-h')==1 or parameterList.count('--help')==1):
    print('DiMHepy is a software by Luca Triboli, version 1.0')
    print('Usage: python3 DiMHepy.py -i pyani_INDIR    -o pyani_OUTDIR    -oss DiMHepy_outImage [option] [arg]')
    print('    or python3 DiMHepy.py -ia AlignmentFile -ip PercentageFile -oss DiMHepy_outImage [option] [arg]')
    print('Options and arguments (and corresponding environment variables):')
    print('-h       : print this help message and exit (also --help)')
    print('-v       : print version number (also --version)')
    print('-i arg   : insert the INDIR of pyani')
    print('-o arg   : insert the OUTDIR of pyani')
    print('-ia arg  : insert the file name of alignment lengths')
    print('-ip arg  : insert the file name of percentage identity)')
    print('-oss arg : insert the file name of the output image')
    print('-s       : show output png file (only in graphic environment)')
    print('-d       : display output interactive window (only in graphic environment)')
    print('-ignDiag : ignore Diagonal')

elif (parameterList.count('-v')==1 or parameterList.count('--version')==1):
    print('Version 1.1')


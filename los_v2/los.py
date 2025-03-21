# This script manages drawing for all categories and export into final tables ready for printing

import pandas as pd
import glob
import os
import random
import openpyxl

kat_folders = glob.glob('./vahy/*')

# we take every weight category, draw contestands from each separately and than save the draw result into separate pre-formated file
for folds in kat_folders:
    vah_folders = glob.glob('./%s/*.xlsx' %folds)

    weights = []
    counts = []

    for vah in vah_folders:
        df = pd.read_excel(vah, index_col=0, header = 0)
        df.reset_index(inplace=True)
         #df.reset_index(inplace=True)
        
        # Logic for random drawing
        # what I actualy do here is creating list of numbers from 1 to lenght - 1, than choosing random number from this list for each row,
        # take out tkat number from our list, assing it to it's row and finaly resorting the table    
        # This is a bit hacky solution, but python's handling of lists allow us to take some shortcuts in sacrifice of time
        ind = []
        for i in range(0, len(df.index)):
            ind.append(i)
            
        index = []
        for row in df.index:
            i = random.randint(0, len(ind)-1)
            x = ind[i]
            #df.at[row, 'index'] = x
            index.append(x)
            ind.remove(x)
            
        df.reindex(index=index)
        df.reset_index(drop= True, inplace=True)
        #df.set_index('index', inplace = True)
        df.sort_index(ascending = True, inplace = True)
        #df.reset_index(inplace=True)
        
        # just getting some names here
        vah_name = os.path.splitext(os.path.basename(vah))[0]
        kat_name = os.path.split(vah)[0]
        kat_name = os.path.split(kat_name)[1]
        
        # Create forlder for saving organized idividual drawed categories if not already present    
        dir = os.path.join(os.getcwd(), 'Los', kat_name)
        if not (os.path.exists(dir) or os.path.isdir(dir)):
            os.mkdir(dir)   
            
        # selecting right template
        count = len(df.index)
        
        # for my use case, I don't think I will ever need to draw more than 32 contestants, but if you do, you can modify this yourself
        if count < 7:
            uf = count
        elif count < 9:
            uf = 8
        elif count < 17:
            uf = 16
        elif count < 33:
            uf = 32
        
        # append table for categories and number of contestants
        weights.append(str(vah_name))
        counts.append(count)

        templateFile = 'Template' + str(uf) + '.xlsx'
        templateDir = os.path.join(os.getcwd(), 'Template', templateFile)
        if not os.path.exists(templateDir):
            if count == 0:
                continue
            print("TEMPLATE " + str(templateDir) + " NOT FOUND")
        else:
            excel = openpyxl.load_workbook(templateDir)
            sheet = excel.active
            
            sheet['A1'] = kat_name
            sheet['E4'] = '- ' + vah_name
            
            # there are multiple conditions where modifying templates would be more suitable than modifying code
            # but man I hate excel so much that I am not willing to touch it now
            start = 6
            letterName = 'B'
            letterClub = 'C'
            if count < 9:
                pass
            elif count < 17:
                start = 3
                letterName= 'M'
                letterClub = 'N'
            elif count < 33:
                start = 2
                letterName = 'O'
                letterClub = 'P'
            
            for i in range(0, count):
                # same thing applies here
                if count == 6:
                    if i >= 3:
                        start = 9
                elif count < 17 and count > 6:
                    if i >= 4:
                        start = 9
                index = str(start + i)

                #sheet[letterName + index] = str(df.at[i, 'Příjmení, jméno'])
                sheet[letterName + index] = str(df.at[i, 'Příjmení']) + ' ' + str(df.at[i, 'Jméno'])
                sheet[letterClub + index] = df.at[i, 'Klub']
            
            #and saving to excel again
            file = vah_name + '.xlsx'
            dir = os.path.join(os.getcwd(), 'Los', kat_name, file)
            excel.save(dir)
        
    kat_name = os.path.split(folds)[1]
    kat_name = os.path.split(kat_name)[1]
    kat_name = os.path.split(kat_name)[1]

    # TODO: Print into file
    
    #print(kat_name + ':',file = f)
    print(kat_name + ':',)

    for i in range(0, len(counts)):
        if counts[i] != 0:
            print(weights[i] + ': ' + str(counts[i]))
            #print(weights[i] + ': ' + str(counts[i]), file ='drawed cats.txt')

    print('')

print("Drawing done")
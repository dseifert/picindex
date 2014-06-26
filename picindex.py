#!/usr/bin/python

import glob
import math
import sys
 
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from math import ceil
from units import unit, scaled_unit


################################################################################

# define the common units
meter  = unit('meter')
cm     = scaled_unit('centimeter', 'meter', 1/100.)
mm     = scaled_unit('millimeter', 'meter', 1/1000.)
inch   = scaled_unit('inch', 'centimeter', 2.54)
pixel  = unit('pixel')

# define common paper sizes
a4     = ( mm(210), mm(297) )
a5     = ( mm(148), mm(210) )
a6     = ( mm(105), mm(148) )
a7     = ( mm(74),  mm(105) )
letter = ( inch(8.5), inch(11) )


################################################################################

"""
Calculate how many pixels are in a length for a given dpi value

length   The length in a defined unit
dpi      The DPI (dots-per-inch) value to use

Returns the number of pixels for @length at this dpi
""" 

def pixels(length, dpi):
	if length.unit == unit('pixel'):
		return int(length)
	else:
		return int( inch(length) * dpi )


################################################################################

"""
Create a picture index.

files            The pictures to index

numberOfColumns  Number of columns in the contact sheet

sheetWidth       Width of the sheet
sheetHeight      Height of the sheet

marginLeft       Margin on the left side of the sheet
marginRight      Margin on the right side of the sheet
marginTop        Margin on the top side of the sheet
marginBottom     Margin on the bottom side of the sheet

output           Output file name

dpi              The dpi (dots-per-inch) to use.
paddingX         The horizontal padding between images
paddingY         The vertical padding between images
title            The title to print (directoryName if empty)
titleFontHeight  Height of the title (0 to suppress title)
labelFontHeight  Height of the labels (0 to suppress labels)
"""

def createPictureIndex(pictures,
                       numberOfColumns,
                       (sheetWidth, sheetHeight),
                       (marginLeft, marginTop, marginRight, marginBottom),
                       output="index.pdf",
                       dpi=150,
                       paddingX=mm(5),
                       paddingY=mm(-1),
                       title="",
                       titleFontHeight=pixel(0),
                       labelFontHeight=pixel(0)
                      ):

	# if no paddingY value is specified, use the paddingX one
	if int(paddingY) == -1:
		paddingY = paddingX

	# convert parameters to pixels
	sheetWidth   = pixels(sheetWidth,   dpi)
	sheetHeight  = pixels(sheetHeight,  dpi)
	print sheetWidth
	print sheetHeight
	marginLeft   = pixels(marginLeft,   dpi)
	marginTop    = pixels(marginTop,    dpi)
	marginRight  = pixels(marginRight,  dpi)
	marginBottom = pixels(marginBottom, dpi)
	paddingX     = pixels(paddingX,     dpi)
	paddingY     = pixels(paddingY,     dpi)
	
	titleFontHeight = pixels(titleFontHeight, dpi)
	labelFontHeight = pixels(labelFontHeight, dpi)

	# calculate the width of an image tile
	printableWidth = sheetWidth - marginLeft - marginRight - (numberOfColumns-1)*paddingX
	tileWidth = int( printableWidth / numberOfColumns )

	# create the sheet with a white background
	card = Image.new('RGB', (sheetWidth, sheetHeight), (255, 255, 255))
	
	# place title
	if titleFontHeight > 0:
		titleFont = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", titleFontHeight)

		draw = ImageDraw.Draw(card)
		(titleWidth, titleHeight) = draw.textsize(title, font=titleFont)
		
		x = int( (sheetWidth - marginRight + marginLeft - titleWidth) / 2 )
		y = marginTop
		draw.text( (x, y), title, font=titleFont, fill=(0, 0, 0))

		nextRowTop = int(marginTop + 1.1*titleFontHeight)
	else:
		nextRowTop = marginTop

	if labelFontHeight > 0:
		labelFont = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", labelFontHeight)

	for index in range(0, len(pictures) ):
		row    = index / numberOfColumns;
		column = index % numberOfColumns;
		
		# adjust beginning of row when we start a new one
		if (column == 0):
			rowTop = nextRowTop

		print "Adding " + pictures[index]

		try:
			# Read in an image and resize appropriately
			image = Image.open(pictures[index])
		except:
			print "---> ERROR: Could not open file " + pictures[index]
			break

		imageWidth, imageHeight = image.size
		tileHeight = imageHeight / (imageWidth / tileWidth)
		tileTop    = rowTop
		tileBottom = rowTop + tileHeight
		tileLeft   = marginLeft + column * (tileWidth + paddingX)
		tileRight  = tileLeft + tileWidth

		image = image.resize( (tileWidth, tileHeight) )
		
		nextRowTop = max(nextRowTop, int(tileBottom + labelFontHeight*1.2 + paddingY))
		card.paste(image, (tileLeft, tileTop, tileRight, tileBottom) )

		draw.text((tileLeft, tileBottom + 2), files[index], font=labelFont, fill=(0, 0, 0) )

	print dpi
	print card.size
	card.save(output, dpi=(dpi, dpi))


################################################################################

if (len(sys.argv) != 2):
	print "Usage: " + sys.argv[0] + " <folder>"
	quit()


directoryName = sys.argv[1];
files = sorted( glob.glob(directoryName + "/IMG_59*.JPG") );
if len(files) <= 18:
	cols = 3
elif len(files) <= 36:
	cols = 4
else:
	cols = 5

print "Found " + str(len(files)) + " images in directory " + directoryName + ", using " + str(cols) + " columns"
createPictureIndex(files, cols, a4, [ mm(20), mm(1), mm(5), mm(5) ],
                   title="Folder " + directoryName,
                   dpi=300,
                   paddingX=mm(8),
                   paddingY=mm(2),
                   titleFontHeight=mm(10),
                   labelFontHeight=mm(3)
                  )


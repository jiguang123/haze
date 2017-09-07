#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image

def filter2d(input_img, filter, frame):
  """filter of the 2-dimension picture"""
  size = len(input_img), len(input_img[0])
  output = []

  for i in xrange(size[0]):
    temp = []
    for j in xrange(size[1]):
      temp.append(filter(input_img, (i, j), frame))

    output.append(temp)

  return output

def minimizeFilter(input_img, point, size):
  """minimize filter for the input image"""
  begin = (point[0] - size[0] / 2, point[0] + size[0] / 2 + 1)
  end = (point[1] - size[1] / 2, point[1] + size[1] / 2 + 1)

  l = []

  for i in xrange(*begin):
    for j in xrange(*end):
      if (i >= 0 and i < len(input_img)) and (j >= 0 and j < len(input_img[0])):
        l.append(input_img[i][j])

  return min(l)

def convertImageToMatrix(image):
  size = image.size
  out = []

  for x in xrange(size[1]):
    temp = []
    for y in xrange(size[0]):
      temp.append(image.getpixel((y, x)))

    out.append(temp)

  return out

def boxFilter(im, radius):
  """box filter for the image of the radius"""
  height, width = len(im), len(im[0])

  imDst = []
  imCum = []

  for x in xrange(height):
    imDst.append([0.0] * width)
    imCum.append([0.0] * width)

  #cumulative sum over Y axis
  for i in xrange(width):
    for j in xrange(height):
      if j == 0:
        imCum[j][i] = im[j][i]
      else:
        imCum[j][i] = im[j][i] + imCum[j - 1][i]

  #difference over Y axis
  for j in xrange(radius + 1):
    for i in xrange(width):
      imDst[j][i] = imCum[j + radius][i]

  for j in xrange(radius + 1, height - radius):
    for i in xrange(width):
      imDst[j][i] = imCum[j + radius][i] - imCum[j - radius - 1][i]

  for j in xrange(height - radius, height):
    for i in xrange(width):
      imDst[j][i] = imCum[height - 1][i] - imCum[j - radius - 1][i]

  #cumulative sum over X axis
  for j in xrange(height):
    for i in xrange(width):
      if i == 0:
        imCum[j][i] = imDst[j][i]
      else:
        imCum[j][i] = imDst[j][i] + imCum[j][i - 1]

  #difference over X axis
  for j in xrange(height):
    for i in xrange(radius + 1):
      imDst[j][i] = imCum[j][i + radius]

  for j in xrange(height):
    for i in xrange(radius + 1, width - radius):
      imDst[j][i] = imCum[j][i + radius] - imCum[j][i - radius - 1]

  for j in xrange(height):
    for i in xrange(width - radius, width):
      imDst[j][i] = imCum[j][width - 1] - imCum[j][i - radius - 1]

  return imDst

def dot(matrix1, matrix2, operation):
  """dot operation for the matrix1 and matrix2"""
  out = []
  size = len(matrix1), len(matrix1[0])

  for x in xrange(size[0]):
    temp = []
    for y in xrange(size[1]):
      temp.append(operation(matrix1[x][y], matrix2[x][y]))

    out.append(temp)

  return out

def guidedFilter(srcImage, guidedImage, radius, epsilon):
  """guided filter for the image
     src image must be gray image
     guided image must be gray image
  """

  size = srcImage.size
  src = convertImageToMatrix(srcImage)
  guided = convertImageToMatrix(guidedImage)

  one = []

  for x in xrange(size[1]):
    one.append([1.0] * size[0])

  n = boxFilter(one, radius)

  plus = lambda x, y: x + y
  minus = lambda x, y: x - y
  multiple = lambda x, y: x * y
  divide = lambda x, y: x / y

  meanI = dot(boxFilter(src, radius), n, divide)
  meanP = dot(boxFilter(guided, radius), n, divide)
  meanIP = dot(boxFilter(dot(src, guided, multiple), radius), n, divide)

  covIP = dot(meanIP, dot(meanI, meanP, multiple), minus)

  meanII = dot(boxFilter(dot(src, src, multiple), radius), n, divide)
  varI = dot(meanII, dot(meanI, meanI, multiple), minus)

  epsilonMatrix = []

  for x in xrange(size[1]):
    epsilonMatrix.append([epsilon] * size[0])

  a = dot(covIP, dot(varI, epsilonMatrix, plus), divide)
  b = dot(meanP, dot(a, meanI, multiple), minus)

  meanA = dot(boxFilter(a, radius), n, divide)
  meanB = dot(boxFilter(b, radius), n, divide)

  return dot(dot(meanA, src, multiple), meanB, plus)





#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PIL import Image
from guidedfilter import *

def getDark(input_img, filter, frame):
  """get dark image from the input image"""
  size = input_img.size
  output = []

  for x in xrange(size[1]):
    temp = []
    for y in xrange(size[0]):
      temp.append(min(input_img.getpixel((y, x))))

    output.append(temp)

  output = filter2d(output, filter, frame)

  output_img = Image.new('L', size)

  for x in xrange(size[1]):
    for y in xrange(size[0]):
      output_img.putpixel((y, x), output[x][y])

  return output_img

def getLight(srcImage, darkImage, cut):
  """get atmospheric light from the picture"""
  size = darkImage.size
  light = []

  for x in xrange(size[0]):
    for y in xrange(size[1]):
      light.append(darkImage.getpixel((x, y)))

  light.sort()
  light.reverse()

  threshold = light[int(cut * len(light))]

  atmosphere = {}

  for x in xrange(size[0]):
    for y in xrange(size[1]):
      if darkImage.getpixel((x, y)) >= threshold:
        atmosphere.update({(x, y): sum(srcImage.getpixel((x, y))) / 3.0})

  pos = sorted(atmosphere.iteritems(), key = lambda item: item[1], reverse = True)[0][0]

  return srcImage.getpixel(pos)

def getTransmission(input_img, light, omiga):
  """get transmission from the picture"""
  size = input_img.size
  output = []

  for x in xrange(size[1]):
    temp = []
    for y in xrange(size[0]):
      temp.append(min(input_img.getpixel((y, x))) / float(min(light)))

    output.append(temp)

  transmission = []

  for x in xrange(size[1]):
    temp = []
    for y in xrange(size[0]):
      temp.append(1 - omiga * minimizeFilter(output, (x, y), (10, 10)))

    transmission.append(temp)

  return transmission

def getRadiance(input_img, transmission, light, t0):
  """get radiance from the picture"""
  size = input_img.size
  output = Image.new('RGB', size)

  for x in xrange(size[1]):
    for y in xrange(size[0]):
      r, g, b = input_img.getpixel((y, x))

      r = int((r - light[0]) / float(max(t0, transmission[x][y])) + light[0])
      g = int((g - light[1]) / float(max(t0, transmission[x][y])) + light[1])
      b = int((b - light[2]) / float(max(t0, transmission[x][y])) + light[2])

      output.putpixel((y, x), (r, g, b))

  return output

def ensure(n):
  if n < 0:
    n = 0

  if n > 255:
    n = 255

  return int(n)

if __name__ == '__main__':
  image = Image.open('4.png')
  image = image.convert('RGB')

  dark = getDark(image, minimizeFilter, (10, 10))

  dark.save('4_dark.png')

  light = getLight(image, dark, 0.001)

  transmission = getTransmission(image, light, 0.9)

  tranImage = Image.new('L', image.size)
  grayImage = image.convert('L')

  for x in xrange(image.size[0]):
    for y in xrange(image.size[1]):
      tranImage.putpixel((x, y), int(transmission[y][x] * 255))

  guided = guidedFilter(grayImage, tranImage, 25, 0.001)

  guidedImage = Image.new('L', image.size)

  for x in xrange(image.size[0]):
    for y in xrange(image.size[1]):
      guidedImage.putpixel((x, y), ensure(guided[y][x]))
      guided[y][x] /= 255.0

  #guidedImage.show()
  guidedImage.save('4_guided.png')

  output = getRadiance(image, guided, light, 0.1)

  output.save('4_haze.png')
import numpy as np
from isimple.video.videodata import VideoAnalyzer
import scipy.optimize
import copy

import matplotlib.pyplot as plt
import time

import sys
import cv2


video = "/home/ybnd/code/SIMPLE/data/shuttle.mp4"
design = "/home/ybnd/code/SIMPLE/data/shuttle.svg"

va = VideoAnalyzer(video, design, prompt_color=False)  # todo: "accept" metadata instead of showing screens
print('\n')

transform_og = copy.copy(va.transform)

area_og = copy.copy(np.sum(va.areas()))

Nf = va.number
frames = [ va.get_frame_at(i, do_warp=False) for i in [0.5] ]

# Optimizing for all masks at once is actually more robust since it wont get into the 'just zoom in all the way'
# territory since the geometry & colors remain important


def target(x, args):
    va_opt = args[0]
    frames_opt = args[1]

    transform = np.array([x[0:3], x[3:6], x[6:9]])

    total_area = 0

    # va.get_frame(do_warp=False)
    for frame in frames_opt:
        total_area -= np.sum(
            va_opt.areas(
                cv2.warpPerspective(frame, transform, (va_opt.shape[1], va_opt.shape[0]))
            )
        )

    # total_area = 0
    # for frame in frames:
    #     total_area -= np.sum(va.areas(va.warp(frame)))

    sys.stdout.write('\r'+f"T(0,0) = {transform[0,0]}, A = {total_area}")
    sys.stdout.flush()

    return total_area


IterPoints = 3
transforms = []
opt_areas = []
dts = []

maxiters = 1+np.linspace(0, IterPoints-1, IterPoints)**2

maxiter = 15

t = time.time()
result = scipy.optimize.minimize(
    target, transform_og.tolist(), [va, frames],
    method='Powell', options={'maxiter': maxiter})
x = result.x

transforms.append(np.array([x[0:3], x[3:6], x[6:9]]))
va.transform = np.array([x[0:3], x[3:6], x[6:9]])
opt_areas.append(np.sum(va.areas()))

dt = time.time() - t

print(f" Success: {result.success} after {result.nit}/{maxiter} iterations in {dt} seconds")
dts.append(dt)



# plt.figure()
# plt.plot(maxiters, transforms)
# plt.show()


# print(dts)

va.transform = transform_og
plt.figure()
va.get_frame_at(0.5, to_hsv=False)
plt.imshow(va.get_overlayed_frame())

va.transform = transforms[0]
plt.figure()
va.get_frame_at(0.5, to_hsv=False)
plt.imshow(va.get_overlayed_frame())

plt.show()

print(f"Transform: {transforms[0]}")

print('Done.')

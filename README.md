# Pictures Optimal Transport


## What is this repository ?


This repository uses optimal transport to compute the transformation between a
picture and another. It uses the same principle as this
repository (https://github.com/nbonneel/network_simplex) except
it is based on POT and this repository contains the full code to generate
such a video.


## How to use it ?

In order to use to it, you should change the configuration to your liking by
modifying conf.py. It includes parameters for the transportation as well as
the computation itself (SLURM parameters if you're using such a scheduler).

### With SLURM

If SLURM is available, you can launch the computation by executing
```
python3 launcher.py
```
This script will create a submission file for SLURM.

### Without SLURM

You can just launch the multiple scripts in the following order:
```
python3 transport.py
python3 make_pics.py
python3 merge_pics.py
```

A notebook is also available, although
it does not contain every feature of the script version (such as easing functions
or the ability to handle more than 2 pictures to create a cycle). As such, the
script version is recommended.


## An example

Here is a few examples computed with 40k points.

<table align="center" border="0">
<tr>
<td><img src="Examples/Monge-Kanto/Monge.jpg" alt="picture of Monge" width="200"/></td>
<td><img src="Examples/Monge-Kanto/Kantorovich.jpg" alt="picture of Kantorovich" width="200"/></td>
<td><img src="Examples/Monge-Kanto/monge-kantorovich.gif" alt="Monge-Kantorovich transport" width="200"/></td>
</tr>

<tr>
<td><img src="Examples/Wojak-Chad/wojak.jpg" alt="picture of Wojak" width="200"/></td>
<td><img src="Examples/Wojak-Chad/colored_chad.png" alt="picture of Chad" width="200"/></td>
<td><img src="Examples/Wojak-Chad/wojak-chad.gif" alt="Wojak-Chad transport" width="200"/></td>
</tr>
</table>

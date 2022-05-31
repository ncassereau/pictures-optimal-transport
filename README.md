# Pictures Optimal Transport


## What is this repository ?

This repository uses optimal transport to compute the transformation between a
picture and another. It is based on
[this code](https://github.com/nbonneel/network_simplex)
through the usage of [POT](https://github.com/PythonOT/POT).
However, this repository contains the full code to generate such a video.


## How to use it ?

In order to use to it, you should change the configuration to your liking by
modifying `conf.py`. It includes parameters for the transportation as well as
the computation itself (SLURM parameters if you're using such a job scheduler).

### With SLURM

If SLURM is available, you can launch the computation by executing the following
in the `src/` folder.
```
python3 launcher.py
```
This script will create a submission file for SLURM.

### Without SLURM

You can just launch the multiple scripts in the following order (inside the `src/` folder):
```
python3 transport.py
python3 make_pics.py
python3 merge_pics.py
```

A notebook is also available, although
it does not contain every feature of the script version (such as easing functions
or the ability to handle more than 2 pictures to create a cycle). As such, the
script version is recommended.


## Examples

Here are a few examples computed with 40k points.

<p align="middle">
<td><img src="Examples/Monge-Kanto/Monge.jpg" title="Gaspard Monge" alt="picture of Monge" width="200"/></td>
<td><img src="Examples/Monge-Kanto/Kantorovich.jpg" title="Leonid Kantorovich" alt="picture of Kantorovich" width="200"/></td>
<td><img src="Examples/Monge-Kanto/monge-kantorovich.gif" alt="Monge-Kantorovich transport" width="200"/></td>
</p>

<hr>

<p align="middle">
<td><img src="Examples/Hatim-Chad/hatim.png" title="Average transformer enjoyer" alt="picture of Wojak" width="200"/></td>
<td><img src="Examples/Hatim-Chad/colored_chad.png" title="Gigachad" alt="picture of Chad" width="200"/></td>
<td><img src="Examples/Hatim-Chad/hatim-chad.gif" alt="Wojak-Chad transport" width="200"/></td>
</p>

<hr>

<p align="middle">
<td><img src="Examples/CharlieTheUnicorn/charlie.png" title="Charlie" alt="picture of Charlie the Unicorn" width="200"/></td>
<td><img src="Examples/CharlieTheUnicorn/pink_unicorn.png" title="Pink" alt="picture of Pink Unicorn" width="200"/></td>
<td><img src="Examples/CharlieTheUnicorn/blue_unicorn.png" title="Blue" alt="picture of Blue Unicorn" width="200"/></td>
<td><img src="Examples/CharlieTheUnicorn/unicorns.gif" alt="Unicorns transport" width="200"/></td>
</p>

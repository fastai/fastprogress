# fastprogress

A fast and simple progress bar for Jupyter Notebook and console. Created by Sylvain Gugger for fast.ai.

Copyright 2017 onwards, fast.ai. Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. A copy of the License is provided in the LICENSE file in this repository.

<img src="https://github.com/fastai/fastprogress/raw/master/images/cifar_train.gif" width="600">

## Install

To install simply use
```
pip install fastprogress
```
or:
```
conda install -c fastai fastprogress
```
Note that this requires python 3.6 or later.

## Usage

### Example 1

Here is a simple example. Each bar takes an iterator as a main argument, and we can specify the second bar is nested with the first by adding the argument `parent=mb`. We can then:
- add a comment in the first bar by changing the value of `mb.main_bar.comment`
- add a comment in the first bar by changing the value of `mb.child.comment`
- write a line between the two bars with `mb.write('message')`

``` python
from fastprogress.fastprogress import master_bar, progress_bar
from time import sleep
mb = master_bar(range(10))
for i in mb:
    for j in progress_bar(range(100), parent=mb):
        sleep(0.01)
        mb.child.comment = f'second bar stat'
    mb.main_bar.comment = f'first bar stat'
    mb.write(f'Finished loop {i}.')
    #mb.update_graph(graphs, x_bounds, y_bounds)
```

<img src="https://github.com/fastai/fastprogress/raw/master/images/pb_basic.gif" width="600">

### Example 2

To add a graph that get plots as the training goes, just use the command `mb.update_graphs`. It will create the figure on its first use. Arguments are:
- `graphs`: a list of graphs to be plotted (each of the form `[x,y]`)
- `x_bounds`: the min and max values of the x axis (if `None`, it will those given by the graphs)
- `y_bounds`: the min and max values of the y axis (if `None`, it will those given by the graphs)

Note that it's best to specify `x_bounds` and `y_bounds`, otherwise the box will change as the loop progresses.

Additionally, we can give the label of each graph via the command `mb.names` (should have as many elements as the graphs argument).

``` python
import numpy as np
mb = master_bar(range(10))
mb.names = ['cos', 'sin']
for i in mb:
    for j in progress_bar(range(100), parent=mb):
        if j%10 == 0:
            k = 100 * i + j
            x = np.arange(0, 2*k*np.pi/1000, 0.01)
            y1, y2 = np.cos(x), np.sin(x)
            graphs = [[x,y1], [x,y2]]
            x_bounds = [0, 2*np.pi]
            y_bounds = [-1,1]
            mb.update_graph(graphs, x_bounds, y_bounds)
            mb.child.comment = f'second bar stat'
    mb.main_bar.comment = f'first bar stat'
    mb.write(f'Finished loop {i}.')
```

<img src="https://github.com/fastai/fastprogress/raw/master/images/pb_cos.gif" width="600">

Here is the rendering in console:

<img src="https://github.com/fastai/fastprogress/raw/master/images/pb_console.gif" width="800">

If the script using this is executed with a redirect to a file, only the results of the `.write` method will be printed in that file.

### Example 3

Here is an example that a typical machine learning training loop can use. It also demonstrates how to set `y_bounds` dynamically.

```
def plot_loss_update(epoch, epochs, mb, train_loss, valid_loss):
    """ dynamically print the loss plot during the training/validation loop.
        expects epoch to start from 1.
    """
    x = range(1, epoch+1)
    y = np.concatenate((train_loss, valid_loss))
    graphs = [[x,train_loss], [x,valid_loss]]
    x_margin = 0.2
    y_margin = 0.05
    x_bounds = [1-x_margin, epochs+x_margin]
    y_bounds = [np.min(y)-y_margin, np.max(y)+y_margin]

    mb.update_graph(graphs, x_bounds, y_bounds)
```

And here is an emulation of a training loop that uses this function:

```
from fastprogress.fastprogress import master_bar, progress_bar
from time import sleep
import numpy as np
import random

epochs = 5
mb = master_bar(range(1, epochs+1))
# optional: graph legend: if not set, the default is 'train'/'valid'
# mb.names = ['first', 'second']
train_loss, valid_loss = [], []
for epoch in mb:
    # emulate train sub-loop
    for batch in progress_bar(range(2), parent=mb): sleep(0.2)
    train_loss.append(0.5 - 0.06 * epoch + random.uniform(0, 0.04))

    # emulate validation sub-loop
    for batch in progress_bar(range(2), parent=mb): sleep(0.2)
    valid_loss.append(0.5 - 0.03 * epoch + random.uniform(0, 0.04))

    plot_loss_update(epoch, epochs, mb, train_loss, valid_loss)
```

And the output:

<img src="https://github.com/fastai/fastprogress/raw/master/images/pb_graph.gif" alt="Output">

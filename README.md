# fast_progress

A fast and simple progress bar for Jupyter Notebook and console. Created by Sylvain Gugger for fast.ai.

Copyright 2017 onwards, fast.ai. Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. A copy of the License is provided in the LICENSE file in this repository.

![](cifar_train.gif)

## Usage

Here is a simple example

``` python
from fast_progress import master_bar, progress_bar
from time import sleep
mb = master_bar(range(10))
for i in mb:
    for j in progress_bar(range(100), parent=mb):
        sleep(0.01)
        mb.child.comment = f'second bar stat'
    mb.first_bar.comment = f'first bar stat'
    mb.write(f'Finished loop {i}.')
    #mb.update_graph(graphs, x_bounds, y_bounds)
```

![](pb_basic.gif)


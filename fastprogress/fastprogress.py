from time import time
from sys import stdout
from warnings import warn

def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook, Spyder or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

IN_NOTEBOOK = isnotebook()
if IN_NOTEBOOK:
    try:
        from ipykernel.kernelapp import IPKernelApp
        from ipywidgets import widgets, IntProgress, HBox, HTML, VBox
        from IPython.display import clear_output, display
        from ipywidgets.widgets.interaction import show_inline_matplotlib_plots
        import matplotlib.pyplot as plt
    except:
        warn("Couldn't import ipywidgets properly, progress bar will use console behavior")
        IN_NOTEBOOK = False

__all__ = ['master_bar', 'progress_bar']

def format_time(t):
    t = int(t)
    h,m,s = t//3600, (t//60)%60, t%60
    if h!= 0: return f'{h}:{m:02d}:{s:02d}'
    else:     return f'{m:02d}:{s:02d}'

class ProgressBar():
    update_every = 0.2

    def __init__(self, gen, total=None, display=True, leave=True, parent=None, auto_update=True):
        self._gen = gen
        self.auto_update = auto_update
        self.total = len(gen) if total is None else total
        if parent is None: self.leave,self.display = leave,display
        else:
            self.leave,self.display=False,False
            parent.add_child(self)
        self.comment = ''
        self.on_iter_begin()
        self.update(0)

    def on_iter_begin(self): pass
    def on_interrupt(self): pass
    def on_iter_end(self): pass
    def on_update(self, val, text): pass

    def __iter__(self):
        self.on_iter_begin()
        self.update(0)
        try:
            for i,o in enumerate(self._gen):
                yield o
                if self.auto_update: self.update(i+1)
        except:
            self.on_interrupt()
            raise
        self.on_iter_end()

    def update(self, val):
        if val == 0:
            self.start_t = self.last_t = time()
            self.pred_t = 0
            self.last_v,self.wait_for = 0,1
            self.update_bar(0)
        elif val >= self.last_v + self.wait_for or val == self.total:
            cur_t = time()
            avg_t = (cur_t - self.start_t) / val
            self.wait_for = max(int(self.update_every / (avg_t+1e-8)),1)
            self.pred_t = avg_t * self.total
            self.last_v,self.last_t = val,cur_t
            self.update_bar(val)

    def update_bar(self, val):
        elapsed_t = self.last_t - self.start_t
        remaining_t = format_time(self.pred_t - elapsed_t)
        elapsed_t = format_time(elapsed_t)
        end = '' if len(self.comment) == 0 else f' {self.comment}'
        self.on_update(val, f'{100 * val/self.total:.2f}% [{val}/{self.total} {elapsed_t}<{remaining_t}{end}]')


class MasterBar():
    def __init__(self, gen, cls, total=None): self.first_bar = cls(gen, total=total, display=False)

    def __iter__(self):
        self.on_iter_begin()
        for o in self.first_bar: yield o
        self.on_iter_end()

    def on_iter_begin(self): pass
    def on_iter_end(self): pass
    def add_child(self, child): pass
    def write(self, line):      pass
    def update_graph(self, graphs, x_bounds, y_bounds): pass


class NBProgressBar(ProgressBar):
    def __init__(self, gen, total=None, display=True, leave=True, parent=None, auto_update=True):
        self.progress,self.text = IntProgress(min=0, max=len(gen) if total is None else total), HTML()
        self.box = HBox([self.progress, self.text])
        super().__init__(gen, total, display, leave, parent, auto_update)

    def on_iter_begin(self):
        if self.display: display(self.box)
        self.is_active=True

    def on_interrupt(self):
        self.progress.bar_style = 'danger'
        self.is_active=False

    def on_iter_end(self):
        if not self.leave: self.box.close()
        self.is_active=False

    def on_update(self, val, text):
        self.text.value = text
        self.progress.value = val


class NBMasterBar(MasterBar):
    names = ['train', 'valid']
    def __init__(self, gen, total=None, hide_graph=False, order=None):
        super().__init__(gen, NBProgressBar, total)
        self.report = []
        self.text = HTML()
        self.vbox = VBox([self.first_bar.box, self.text])
        if order is None: order = ['pb1', 'text', 'pb2', 'graph']
        self.inner_dict = {'pb1':self.first_bar.box, 'text':self.text}
        self.hide_graph,self.order = hide_graph,order

    def on_iter_begin(self):
        self.start_t = self.last_t = time()
        display(self.vbox)

    def on_iter_end(self):
        #if hasattr(self, 'fig'): self.fig.clear()
        total_time = format_time(time() - self.start_t)
        end_report = f'Total time: {total_time}\n'
        max_len = 0
        for item in self.report:
            if len(item[0]) > max_len: max_len = len(item[0])
        for item in self.report:
            ending = f'  ({item[1]})\n' if item[1] != '' else '\n'
            end_report += item[0] + (' ' * (max_len-len(item[0]))) + ending
        self.vbox.close()
        print(end_report)

    def add_child(self, child):
        self.child = child
        self.inner_dict['pb2'] = self.child.box
        if hasattr(self,'out'): self.show(['pb1', 'pb2', 'text', 'graph'])
        else:                   self.show(['pb1', 'pb2', 'text'])

    def show(self, child_names):
        to_show = [name for name in self.order if name in child_names]
        self.vbox.children = [self.inner_dict[n] for n in to_show]

    def write(self, line):
        if hasattr(self, 'last_t'):
            cur_time = time()
            elapsed_time = format_time(cur_time - self.last_t)
            self.last_t = cur_time
        else: elapsed_time = ''
        self.report.append([line, elapsed_time])
        self.text.value += line + '<p>'

    def update_graph(self, graphs, x_bounds=None, y_bounds=None):
        if self.hide_graph: return
        self.out = widgets.Output()
        if not hasattr(self, 'fig'):
            self.fig, self.ax = plt.subplots(1, figsize=(6,4))
        self.out = widgets.Output()
        self.inner_dict['graph'] = self.out
        self.ax.clear()
        if len(self.names) < len(graphs): self.names += [''] * (len(graphs) - len(self.names))
        for g,n in zip(graphs,self.names): self.ax.plot(*g, label=n)
        self.ax.legend(loc='upper right')
        if x_bounds is not None: self.ax.set_xlim(*x_bounds)
        if y_bounds is not None: self.ax.set_ylim(*y_bounds)
        with self.out:
            clear_output(wait=True)
            display(self.ax.figure)
        if hasattr(self,'child') and self.child.is_active: self.show(['pb1', 'pb2', 'text', 'graph'])
        else: self.show(['pb1', 'text', 'graph'])


class ConsoleProgressBar(ProgressBar):
    length:int=50
    fill:str='█'

    def __init__(self, gen, total=None, display=True, leave=True, parent=None, auto_update=True):
        self.max_len,self.prefix = 0,''
        super().__init__(gen, total, display, leave, parent, auto_update)

    def on_iter_end(self):
        if not self.leave and printing():
            print(f'\r{self.prefix}' + ' ' * (self.max_len - len(f'\r{self.prefix}')), end = '\r')

    def on_update(self, val, text):
        if self.display:
            filled_len = int(self.length * val // self.total)
            bar = self.fill * filled_len + '-' * (self.length - filled_len)
            to_write = f'\r{self.prefix} |{bar}| {text}'
            if len(to_write) > self.max_len: self.max_len=len(to_write)
            if printing(): print(to_write, end = '\r')


class ConsoleMasterBar(MasterBar):
    def __init__(self, gen, total=None, hide_graph=False, order=None):
        super().__init__(gen, ConsoleProgressBar, total)

    def add_child(self, child):
        self.child = child
        self.child.prefix = f'Epoch {self.first_bar.last_v+1}/{self.first_bar.total} :'
        self.child.display = True

    def write(self, line): print(line)


NO_BAR = False

def printing():
    return False if NO_BAR else (stdout.isatty() or IN_NOTEBOOK)

if IN_NOTEBOOK: master_bar, progress_bar = NBMasterBar, NBProgressBar
else:           master_bar, progress_bar = ConsoleMasterBar, ConsoleProgressBar

def force_console_behavior():
    return ConsoleMasterBar, ConsoleProgressBar

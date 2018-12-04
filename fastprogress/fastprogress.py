from time import time
from sys import stdout
from warnings import warn

def isnotebook():
    try:
        from google import colab
        return True
    except:
        pass
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
        from IPython.display import clear_output, display, HTML
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
        self.parent = parent
        if parent is None: self.leave,self.display = leave,display
        else:
            self.leave,self.display=False,False
            parent.add_child(self)
        self.comment = ''
        if not self.auto_update:
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
            if not self.auto_update and val >= self.total:
                self.on_iter_end()

    def update_bar(self, val):
        elapsed_t = self.last_t - self.start_t
        remaining_t = format_time(self.pred_t - elapsed_t)
        elapsed_t = format_time(elapsed_t)
        end = '' if len(self.comment) == 0 else f' {self.comment}'
        if self.total == 0:
            warn("Your generator is empty.")
            self.on_update(0, '100% [0/0]')
        else: self.on_update(val, f'{100 * val/self.total:.2f}% [{val}/{self.total} {elapsed_t}<{remaining_t}{end}]')


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

def html_progress_bar(value, total, label, interrupted=False):
    bar_style = 'progress-bar-interrupted' if interrupted else ''
    return f"""
    <div>
        <style>
            /* Turns off some styling */
            progress {{
                /* gets rid of default border in Firefox and Opera. */
                border: none;
                /* Needs to be in here for Safari polyfill so background images work as expected. */
                background-size: auto;
            }}
            .progress-bar-interrupted, .progress-bar-interrupted::-webkit-progress-bar {{
                background: #F44336;
            }}
        </style>
      <progress value='{value}' class='{bar_style}' max='{total}', style='width:300px; height:20px; vertical-align: middle;'></progress>
      {label}
    </div>
    """

def text2html_table(lines):
    html_code = f"<table style='width:{max(300, 75*len(lines[0]))}px; margin-bottom:10px'>\n"
    for line in lines:
        html_code += "  <tr>\n"
        html_code += "\n".join([f"    <th>{o}</th>" for o in line if len(o) >= 1])
        html_code += "\n  </tr>\n"
    return html_code + "</table>\n"

class NBProgressBar(ProgressBar):
    def __init__(self, gen, total=None, display=True, leave=True, parent=None, auto_update=True):
        self.progress = html_progress_bar(0, len(gen) if total is None else total, "")
        super().__init__(gen, total, display, leave, parent, auto_update)

    def on_iter_begin(self):
        if self.display:
            self.out = display(HTML(self.progress), display_id=True)
        self.is_active=True

    def on_interrupt(self):
        if self.parent is not None: self.parent.on_interrupt()
        self.on_update(0, 'Interrupted', interrupted=True)
        self.on_iter_end()

    def on_iter_end(self):
        if not self.leave and self.display: clear_output()
        self.is_active=False

    def on_update(self, val, text, interrupted=False):
        self.progress = html_progress_bar(val, self.total, text, interrupted)
        if self.display:
            self.out.update(HTML(self.progress))
        elif self.parent is not None: self.parent.show()

class NBMasterBar(MasterBar):
    names = ['train', 'valid']
    def __init__(self, gen, total=None, hide_graph=False, order=None, clean_on_interrupt=False):
        super().__init__(gen, NBProgressBar, total)
        self.report, self.clean_on_interrupt = [], clean_on_interrupt
        self.text,self.lines = "",[]
        self.html_code = '\n'.join([self.first_bar.progress, self.text])
        if order is None: order = ['pb1', 'text', 'pb2']
        self.inner_dict = {'pb1':self.first_bar.progress, 'text':self.text}
        self.hide_graph,self.order = hide_graph,order

    def on_iter_begin(self):
        self.start_t = time()
        self.out = display(HTML(self.html_code), display_id=True)

    def on_interrupt(self):
        if self.clean_on_interrupt: clear_output()

    def on_iter_end(self):
        plt.close()
        if hasattr(self, 'fig'): self.out2.update(self.fig)
        total_time = format_time(time() - self.start_t)
        self.out.update(HTML(f'Total time: {total_time} <p>' + self.text))

    def add_child(self, child):
        self.child = child
        self.inner_dict['pb2'] = self.child.progress
        self.show()

    def show(self):
        self.inner_dict['pb1'], self.inner_dict['text'] = self.first_bar.progress, self.text
        if 'pb2' in self.inner_dict: self.inner_dict['pb2'] = self.child.progress
        to_show = [name for name in self.order if name in self.inner_dict.keys()]
        self.html_code = '\n'.join([self.inner_dict[n] for n in to_show])
        self.out.update(HTML(self.html_code))

    def write(self, line, table=False):
        if not table: self.text += line + "<p>"
        else:
            self.lines.append(line)
            self.text = text2html_table(self.lines)

    def show_imgs(self, imgs, titles=None, cols=4, imgsize=4, figsize=None):
        if self.hide_graph: return
        rows = len(imgs)//cols if len(imgs)%cols == 0 else len(imgs)//cols + 1
        plt.close()
        if figsize is None: figsize = (imgsize*cols, imgsize*rows)
        self.fig, axs = plt.subplots(rows, cols, figsize=figsize)
        if titles is None: titles = [None] * len(imgs)
        for img, ax, title in zip(imgs, axs.flatten(), titles): img.show(ax=ax, title=title)
        for ax in axs.flatten()[len(imgs):]: ax.axis('off')
        if not hasattr(self, 'out2'): self.out2 = display(self.fig, display_id=True)
        else: self.out2.update(self.fig)

    def update_graph(self, graphs, x_bounds=None, y_bounds=None):
        if self.hide_graph: return
        if not hasattr(self, 'fig'):
            self.fig, self.ax = plt.subplots(1, figsize=(6,4))
            self.out2 = display(self.ax.figure, display_id=True)
        self.ax.clear()
        if len(self.names) < len(graphs): self.names += [''] * (len(graphs) - len(self.names))
        for g,n in zip(graphs,self.names): self.ax.plot(*g, label=n)
        self.ax.legend(loc='upper right')
        if x_bounds is not None: self.ax.set_xlim(*x_bounds)
        if y_bounds is not None: self.ax.set_ylim(*y_bounds)
        self.out2.update(self.ax.figure)

class ConsoleProgressBar(ProgressBar):
    length:int=50
    fill:str='█'

    def __init__(self, gen, total=None, display=True, leave=True, parent=None, auto_update=True):
        self.max_len,self.prefix = 0,''
        super().__init__(gen, total, display, leave, parent, auto_update)

    def on_interrupt(self):
        self.on_iter_end()

    def on_iter_end(self):
        if not self.leave and printing():
            print(f'\r{self.prefix}' + ' ' * (self.max_len - len(f'\r{self.prefix}')), end = '\r')

    def on_update(self, val, text):
        if self.display:
            filled_len = int(self.length * val // self.total)
            bar = self.fill * filled_len + '-' * (self.length - filled_len)
            to_write = f'\r{self.prefix} |{bar}| {text}'
            if len(to_write) > self.max_len: self.max_len=len(to_write)
            if printing(): WRITER_FN(to_write, end = '\r')

class ConsoleMasterBar(MasterBar):
    def __init__(self, gen, total=None, hide_graph=False, order=None, clean_on_interrupt=False):
        super().__init__(gen, ConsoleProgressBar, total)

    def add_child(self, child):
        self.child = child
        self.child.prefix = f'Epoch {self.first_bar.last_v+1}/{self.first_bar.total} :'
        self.child.display = True

    def write(self, line, table=False):
        if table:
            text = ''
            if not hasattr(self, 'names'):
                self.names = [name + ' ' * (8-len(name)) if len(name) < 8 else name for name in line]
                text = ''.join(self.names)
            else:
                for (t,name) in zip(line,self.names): text += t + ' ' * (len(name)-len(t))
            WRITER_FN(text)
        else: WRITER_FN(line)

    def show_imgs(*args): pass
    def update_graph(*args): pass

NO_BAR = False
WRITER_FN = print

def printing():
    return False if NO_BAR else (stdout.isatty() or IN_NOTEBOOK)

if IN_NOTEBOOK: master_bar, progress_bar = NBMasterBar, NBProgressBar
else:           master_bar, progress_bar = ConsoleMasterBar, ConsoleProgressBar

def force_console_behavior():
    return ConsoleMasterBar, ConsoleProgressBar

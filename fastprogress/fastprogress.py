from time import time
from sys import stdout
from warnings import warn
import shutil,os

__all__ = ['master_bar', 'progress_bar', 'IN_NOTEBOOK', 'force_console_behavior', 'workaround_empty_console_output']

CLEAR_OUTPUT = False
NO_BAR = False
WRITER_FN = print
FLUSH = True
SAVE_PATH = None
SAVE_APPEND = False
MAX_COLS = 160

def isnotebook():
    try:
        from google import colab
        return True
    except: pass
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            # Jupyter notebook, Spyder or qtconsole
            import IPython
            return IPython.__version__ >= '6.0.0'
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
        self.last_v = 0
        if parent is None: self.leave,self.display = leave,display
        else:
            self.leave,self.display=False,False
            parent.add_child(self)
        self.comment = ''
        self._begun = False
        if not self.auto_update: self.update(0)

    def on_iter_begin(self): self._begun = True
    def on_interrupt(self): pass
    def on_iter_end(self): pass
    def on_update(self, val, text): pass

    def __iter__(self):
        self.update(0)
        try:
            for i,o in enumerate(self._gen):
                if i >= self.total: break
                yield o
                if self.auto_update: self.update(i+1)
        except:
            self.on_interrupt()
            raise
        self.on_iter_end()

    def update(self, val):
        if not self._begun: self.on_iter_begin()
        if val == 0:
            self.start_t = self.last_t = time()
            self.pred_t,self.last_v,self.wait_for = 0,0,1
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
    def __init__(self, gen, cls, total=None): 
        self._begun=False
        self.first_bar = cls(gen, total=total, display=False)

    def __iter__(self):
        self.on_iter_begin()
        for o in self.first_bar: yield o
        self.on_iter_end()

    def on_iter_begin(self): 
        self._begun=True
        self.start_t = time()
        
    def on_iter_end(self): pass
    def add_child(self, child): pass
    def write(self, line):      pass
    def update_graph(self, graphs, x_bounds, y_bounds): pass
    
    def update(self, val): 
        if not self._begun: self.on_iter_begin()
        self.first_bar.update(val)

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

def text2html_table(items):
    "Put the texts in `items` in an HTML table."
    html_code = f"""<table border="1" class="dataframe">\n"""
    html_code += f"""  <thead>\n    <tr style="text-align: left;">\n"""
    for i in items[0]: html_code += f"      <th>{i}</th>\n"
    html_code += f"    </tr>\n  </thead>\n  <tbody>\n"
    for line in items[1:]:
        html_code += "    <tr>\n"
        for i in line: html_code += f"      <td>{i}</td>\n"
        html_code += "    </tr>\n"
    html_code += "  </tbody>\n</table><p>"
    return html_code

class NBProgressBar(ProgressBar):
    def __init__(self, gen, total=None, display=True, leave=True, parent=None, auto_update=True):
        self.progress = html_progress_bar(0, len(gen) if total is None else total, "")
        super().__init__(gen, total, display, leave, parent, auto_update)

    def on_iter_begin(self):
        super().on_iter_begin()
        if self.display: self.out = display(HTML(self.progress), display_id=True)
        self.is_active=True

    def on_interrupt(self):
        self.on_update(0, 'Interrupted', interrupted=True)
        if self.parent is not None: self.parent.on_interrupt()
        self.on_iter_end()

    def on_iter_end(self):
        if not self.leave and self.display:
            if CLEAR_OUTPUT: clear_output()
            else: self.out.update(HTML(''))
        self.is_active=False

    def on_update(self, val, text, interrupted=False):
        self.progress = html_progress_bar(val, self.total, text, interrupted)
        if self.display: self.out.update(HTML(self.progress))
        elif self.parent is not None: self.parent.show()

class NBMasterBar(MasterBar):
    names = ['train', 'valid']
    def __init__(self, gen, total=None, hide_graph=False, order=None, clean_on_interrupt=False, total_time=False):
        super().__init__(gen, NBProgressBar, total)
        self.report,self.clean_on_interrupt,self.total_time = [],clean_on_interrupt,total_time
        self.text,self.lines = "",[]
        self.html_code = '\n'.join([self.first_bar.progress, self.text])
        if order is None: order = ['pb1', 'text', 'pb2']
        self.inner_dict = {'pb1':self.first_bar.progress, 'text':self.text}
        self.hide_graph,self.order = hide_graph,order

    def on_iter_begin(self):
        super().on_iter_begin()
        self.out = display(HTML(self.html_code), display_id=True)

    def on_interrupt(self):
        if self.clean_on_interrupt: self.out.update(HTML(''))

    def on_iter_end(self):
        if hasattr(self, 'imgs_fig'):
            plt.close()
            self.imgs_out.update(self.imgs_fig)
        if hasattr(self, 'graph_fig'):
            plt.close()
            self.graph_out.update(self.graph_fig)
        total_time = format_time(time() - self.start_t)
        if self.text.endswith('<p>'): self.text = self.text[:-3]
        if self.total_time: self.text = f'Total time: {total_time} <p>' + self.text
        self.out.update(HTML(self.text))

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
        self.imgs_fig, imgs_axs = plt.subplots(rows, cols, figsize=figsize)
        if titles is None: titles = [None] * len(imgs)
        for img, ax, title in zip(imgs, imgs_axs.flatten(), titles): img.show(ax=ax, title=title)
        for ax in imgs_axs.flatten()[len(imgs):]: ax.axis('off')
        if not hasattr(self, 'imgs_out'): self.imgs_out = display(self.imgs_fig, display_id=True)
        else: self.imgs_out.update(self.imgs_fig)

    def update_graph(self, graphs, x_bounds=None, y_bounds=None, figsize=(6,4)):
        if self.hide_graph: return
        if not hasattr(self, 'graph_fig'):
            self.graph_fig, self.graph_ax = plt.subplots(1, figsize=figsize)
            self.graph_out = display(self.graph_ax.figure, display_id=True)
        self.graph_ax.clear()
        if len(self.names) < len(graphs): self.names += [''] * (len(graphs) - len(self.names))
        for g,n in zip(graphs,self.names): self.graph_ax.plot(*g, label=n)
        self.graph_ax.legend(loc='upper right')
        if x_bounds is not None: self.graph_ax.set_xlim(*x_bounds)
        if y_bounds is not None: self.graph_ax.set_ylim(*y_bounds)
        self.graph_out.update(self.graph_ax.figure)

class ConsoleProgressBar(ProgressBar):
    fill:str='█'
    end:str='\r'

    def __init__(self, gen, total=None, display=True, leave=True, parent=None, auto_update=True, txt_len=60):
        self.cols,_ = shutil.get_terminal_size((100, 40))
        if self.cols > MAX_COLS: self.cols=MAX_COLS
        self.length = self.cols-txt_len
        self.max_len,self.prefix = 0,''
        try: print(self.fill, end='\r', flush=FLUSH)
        except: self.fill = 'X'
        super().__init__(gen, total, display, leave, parent, auto_update)

    def on_interrupt(self):
        self.on_iter_end()

    def on_iter_end(self):
        if not self.leave and printing():
            print(f'\r{self.prefix}' + ' ' * (self.max_len - len(f'\r{self.prefix}')), end='\r', flush=FLUSH)

    def on_update(self, val, text):
        if self.display:
            if self.length > self.cols-len(text)-len(self.prefix)-4:
                self.length = self.cols-len(text)-len(self.prefix)-4
            filled_len = int(self.length * val // self.total) if self.total else 0
            bar = self.fill * filled_len + '-' * (self.length - filled_len)
            to_write = f'\r{self.prefix} |{bar}| {text}'
            if val >= self.total: end = '\r'
            else: end = self.end
            if len(to_write) > self.max_len: self.max_len=len(to_write)
            if printing(): WRITER_FN(to_write, end=end, flush=FLUSH)

class ConsoleMasterBar(MasterBar):
    def __init__(self, gen, total=None, hide_graph=False, order=None, clean_on_interrupt=False, total_time=False):
        super().__init__(gen, ConsoleProgressBar, total)
        self.total_time = total_time

    def add_child(self, child):
        self.child = child
        self.child.prefix = f'Epoch {self.first_bar.last_v+1}/{self.first_bar.total} :'
        self.child.display = True

    def on_iter_begin(self):
        super().on_iter_begin()
        if SAVE_PATH is not None and os.path.exists(SAVE_PATH) and not SAVE_APPEND:
            with open(SAVE_PATH, 'w') as f: f.write('')

    def write(self, line, table=False):
        if table:
            text = ''
            if not hasattr(self, 'names'):
                self.names = [name + ' ' * (8-len(name)) if len(name) < 8 else name for name in line]
                text = '  '.join(self.names)
            else:
                for (t,name) in zip(line,self.names): text += t + ' ' * (2 + len(name)-len(t))
            print_and_maybe_save(text)
        else: print_and_maybe_save(line)
        if self.total_time:
            total_time = format_time(time() - self.start_t)
            print_and_maybe_save(f'Total time: {total_time}')

    def show_imgs(*args): pass
    def update_graph(*args): pass

def print_and_maybe_save(line):
    WRITER_FN(line)
    if SAVE_PATH is not None:
        attr = "a" if os.path.exists(SAVE_PATH) else "w"
        with open(SAVE_PATH, attr) as f: f.write(line + '\n')

def printing():
    return False if NO_BAR else (stdout.isatty() or IN_NOTEBOOK)

if IN_NOTEBOOK: master_bar, progress_bar = NBMasterBar, NBProgressBar
else:           master_bar, progress_bar = ConsoleMasterBar, ConsoleProgressBar

def force_console_behavior():
    return ConsoleMasterBar, ConsoleProgressBar

def workaround_empty_console_output():
    """Changes console output behaviour to correctly show progress in consoles not recognizing \r at the end of line
    This helps in terminals like PyCharm Console etc."""
    ConsoleProgressBar.end = ''

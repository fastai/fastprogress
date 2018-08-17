from ipywidgets import IntProgress, HBox, HTML, VBox
from time import time

def format_time(t):
    t = int(t)
    h,m,s = t//3600, (t//60)%60, t%60
    if h!= 0: return f'{h}:{m:02d}:{s:02d}'
    else:     return f'{m:02d}:{s:02d}'


class ProgressBar():
    update_every = 0.2

    def __init__(self, gen, display=True, leave=True, parent=None):
        self._gen,self.total = gen,len(gen)
        if parent is None: self.leave,self.display = leave,display
        else:
            self.leave,self.display=False,False
            parent.add_child(self)
        self.comment = ''

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
                self.update(i+1)
        except: self.on_interrupt()
        self.on_iter_end()

    def update(self, val):
        if val == 0:
            self.start_t = self.last_t = time()
            self.pred_t = 0
            self.last_v,self.wait_for = 0,1
            self.update_bar(0)
        elif val >= self.last_v + self.wait_for:
            cur_t = time()
            avg_t = (cur_t - self.start_t) / val
            self.wait_for = max(int(self.update_every / avg_t),1)
            self.pred_t = avg_t * self.total
            self.last_v,self.last_t = val,cur_t
            self.update_bar(val)

    def update_bar(self, val):
        elapsed_t = self.last_t - self.start_t
        remaining_t = format_time(self.pred_t - elapsed_t)
        elapsed_t = format_time(elapsed_t)
        end = '' if len(self.comment) == 0 else f' {self.comment}'
        self.on_update(val, f'{100 * val/self.total:.2f}% [{val}/{self.total} {elapsed_t}<{remaining_t}{end}]')


class NBProgressBar(ProgressBar):
    def __init__(self,gen, display=True, leave=True, parent=None):
        self.progress,self.text = IntProgress(min=0, max=len(gen)), HTML()
        self.box = HBox([self.progress, self.text])
        super().__init__(gen, display, leave, parent)

    def on_iter_begin(self): if self.display: display(self.box)
    def on_interrupt(self): self.progress.bar_style = 'danger'
    def on_iter_end(self):
        if not self.leave: self.box.close()

    def on_update(self, val, text):
        self.text.value = text
        self.progress.value = val


class ConsoleProgressBar(ProgressBar):
    length:int=50
    fill:str='█'

    def __init__(self,gen, display=True, leave=True, parent=None):
        self.max_len,self.prefix = 0,''
        super().__init__(gen, display, leave, parent)

    def on_iter_end(self):
        if not self.leave:
            print(f'\r{self.prefix}' + ' ' * (self.max_len - len(f'\r{self.prefix}')), end = '\r')

    def on_update(self, val, text):
        if self.display:
            filled_len = int(self.length * val // self.total)
            bar = self.fill * filled_len + '-' * (self.length - filled_len)
            to_write = f'\r{self.prefix} |{bar}| {text}'
            if len(to_write) > self.max_len: self.max_len=len(to_write)
            print(to_write, end = '\r')


class MasterBar():
    def __init__(self, gen, cls): self.first_bar = cls(gen, display=False)

    def on_iter_begin(self): pass

    def __iter__(self):
        self.on_iter_begin()
        for o in self.first_bar: yield o

    def add_child(self, child): pass
    def write(self, line):      pass


class NBMasterBar(MasterBar):
    def __init__(self, gen):
        super().__init__(gen, NBProgressBar)
        self.text = HTML()
        self.vbox = VBox([self.first_bar.box, self.text])

    def on_iter_begin(self): display(self.vbox)

    def add_child(self, child):
        self.child = child
        self.vbox.children = [self.first_bar.box, self.text, child.box]

    def write(self, line): self.text.value += line + '<p>'


class ConsoleMasterBar(MasterBar):
    def __init__(self, gen): super().__init__(gen, ConsoleProgressBar)

    def add_child(self, child):
        self.child = child
        self.child.prefix = f'Epoch {self.first_bar.last_v+1}/{self.first_bar.total} :'
        self.child.display = True

    def write(self, line): print(line)


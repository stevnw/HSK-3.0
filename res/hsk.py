import wx
import csv
import random
import pygame.mixer

class HSKPanel(wx.Panel):
    def __init__(self, parent, band, content_type, random_mode):
        super().__init__(parent, size=(500, 600))
        pygame.mixer.init()
        self.band = band
        self.content_type = content_type
        self.random_mode = random_mode
        self.data = []
        self.current_index = 0
        self.current_answer = None
        self.current_row = None
        self.buttons = []
        self.config = {
            'characters': 'simplified',
            'readings': 'pinyin'
        }
        
        self.load_config()
        self.init_ui()
        self.load_data()
        self.NewQuestion()

    def init_ui(self):
        self.SetBackgroundColour(wx.WHITE)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Hanzi stuff
        self.char_display = wx.StaticText(self, style=wx.ALIGN_CENTER)
        font = wx.Font(72, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.char_display.SetFont(font)
        
        # Meaning stuff
        self.meaning_display = wx.StaticText(self, style=wx.ALIGN_CENTER|wx.ST_ELLIPSIZE_END)
        meaning_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.meaning_display.SetFont(meaning_font)
        
        # Container shieeet
        text_sizer = wx.BoxSizer(wx.VERTICAL)
        text_sizer.AddStretchSpacer(1)
        text_sizer.Add(self.char_display, 0, wx.ALIGN_CENTER|wx.ALL, 20)
        text_sizer.Add(self.meaning_display, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.RIGHT, 20)
        text_sizer.AddStretchSpacer(1)
        
        # Answer button stuffs
        grid = wx.GridSizer(2, 2, 5, 5)
        for _ in range(4):
            btn = wx.Button(self)
            btn.Bind(wx.EVT_BUTTON, self.OnButtonClick)
            self.buttons.append(btn)
            grid.Add(btn, 1, wx.EXPAND)
        
        vbox.Add(text_sizer, 3, wx.EXPAND)
        vbox.Add(grid, 2, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(vbox)

    def set_random_mode(self, random_mode):
        self.random_mode = random_mode
        self.current_index = 0
        self.NewQuestion()

    def update_content(self, band, content_type):
        self.band = band
        self.content_type = content_type
        self.current_index = 0
        self.load_data()
        self.NewQuestion()

    def reload_config(self):
        self.load_config()
        self.current_index = 0
        self.load_data()
        self.NewQuestion()

    def load_config(self):
        config_path = 'res/config.txt'
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip().strip('"\'')
                        if key in self.config:
                            self.config[key] = value.lower()
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")

    def load_data(self):
        self.data = []
        filename = f'res/band{self.band}_{self.content_type}.csv'
        char_col = 0 if self.config['characters'] == 'simplified' else 1
        reading_col = 2 if self.config['readings'] == 'pinyin' else 3
        
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    self.data.append((
                        row[char_col],
                        row[reading_col],
                        row[5],
                        row[4]
                    ))
        except FileNotFoundError:
            print(f"Data file {filename} not found!")
            self.data = []

    def NewQuestion(self):
        if not self.data:
            return
        
        for btn in self.buttons:
            btn.SetBackgroundColour(wx.NullColour)
            btn.Enable()

        if self.random_mode:
            self.current_row = random.choice(self.data)
        else:
            self.current_row = self.data[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.data)
        
        self.current_answer = self.current_row[1]
        self.char_display.SetLabel(self.current_row[0])
        self.meaning_display.SetLabel(self.current_row[3])
        
        self.Freeze()
        max_width = self.GetSize().width - 40
        self.meaning_display.Wrap(max_width)
        self.Layout()
        self.Thaw()
        
        if self.random_mode:
            all_readings = [row[1] for row in self.data]
            wrong_answers = [p for p in all_readings if p != self.current_answer]
            answers = random.sample(wrong_answers, 3) + [self.current_answer]
            random.shuffle(answers)
        else:
            next_indices = [
                (self.current_index + i) % len(self.data)
                for i in range(1, 4)
            ]
            answers = [self.current_answer] + [self.data[i][1] for i in next_indices]
            random.shuffle(answers)
        
        for btn, answer in zip(self.buttons, answers):
            btn.SetLabel(answer)

    def OnButtonClick(self, event):
        btn = event.GetEventObject()
        if btn.GetLabel() == self.current_answer:
            btn.SetBackgroundColour(wx.Colour(0, 255, 0))
            for b in self.buttons:
                b.Disable()
            
            sound = self.play_correct_sound()
            if sound:
                length = int(sound.get_length() * 1000)
                wx.CallLater(length, self.NewQuestion)
        else:
            btn.SetBackgroundColour(wx.Colour(255, 0, 0))
            self.play_wrong_sound()

    def play_correct_sound(self):
        try:
            sound = pygame.mixer.Sound(self.current_row[2])
            sound.play()
            return sound
        except Exception as e:
            print(f"Error playing sound: {e}")
            return None

    def play_wrong_sound(self):
        try:
            sound = pygame.mixer.Sound('res/wrong.wav')
            sound.play()
        except Exception as e:
            print(f"Error playing wrong sound: {e}")

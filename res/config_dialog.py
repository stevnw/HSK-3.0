import wx

class ConfigDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Configuration", size=(300, 200),
                         style=wx.DEFAULT_DIALOG_STYLE & ~wx.RESIZE_BORDER)
        self.config = {}
        self.load_current_config()
        self.init_ui()
        self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_OK)
        
    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Characters type selector dropdown thingie
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        lbl_char = wx.StaticText(panel, label="Characters:", size=(90, -1))
        self.char_choice = wx.Choice(panel, choices=["simplified", "traditional"])
        self.char_choice.SetStringSelection(self.config.get('characters', 'simplified'))
        hbox1.Add(lbl_char, 0, wx.ALIGN_CENTER_VERTICAL)
        hbox1.Add(self.char_choice, 1, wx.EXPAND|wx.LEFT, 10)

        # Same but readings
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        lbl_read = wx.StaticText(panel, label="Readings:", size=(90, -1))
        self.read_choice = wx.Choice(panel, choices=["pinyin", "zhuyin"])
        self.read_choice.SetStringSelection(self.config.get('readings', 'pinyin'))
        hbox2.Add(lbl_read, 0, wx.ALIGN_CENTER_VERTICAL)
        hbox2.Add(self.read_choice, 1, wx.EXPAND|wx.LEFT, 10)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()

        vbox.Add(hbox1, 1, wx.EXPAND|wx.ALL, 10)
        vbox.Add(hbox2, 1, wx.EXPAND|wx.ALL, 10)
        vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER|wx.BOTTOM, 10)
        
        panel.SetSizer(vbox)
        self.Center()

    def on_save(self, event):
        if self.SaveConfig():
            event.Skip()

    def load_current_config(self):
        try:
            with open('res/config.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip().strip('"\'').lower()
                        self.config[key] = value
        except Exception as e:
            print(f"Error loading config: {e}")

    def GetConfig(self):
        return {
            'characters': self.char_choice.GetStringSelection(),
            'readings': self.read_choice.GetStringSelection()
        }

    def SaveConfig(self):
        config = self.GetConfig()
        try:
            with open('res/config.txt', 'w') as f:
                f.write("# simplified or traditional\n")
                f.write(f"characters = '{config['characters']}'\n\n")
                f.write("# pinyin or zhuyin\n")
                f.write(f"readings = '{config['readings']}'\n")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

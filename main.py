import wx
from res.hsk import HSKPanel
from res.config_dialog import ConfigDialog

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="HSK 3.0 Practice", size=(800, 1000))
        self.SetIcon(wx.Icon('res/icon.xpm'))
        self.current_band = 1
        self.content_type = 'char'
        self.random_mode = True
        
        self.control_panel = wx.Panel(self)
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Band and Content type selection stuff
        self.band_choice = wx.Choice(self.control_panel, choices=[str(i) for i in range(1, 7)])
        self.band_choice.SetSelection(0)
        self.band_choice.Bind(wx.EVT_CHOICE, self.on_band_change)
        
        self.type_choice = wx.Choice(self.control_panel, choices=['Characters', 'Vocabulary'])
        self.type_choice.SetSelection(0)
        self.type_choice.Bind(wx.EVT_CHOICE, self.on_type_change)
        
        # Random mode toggle
        self.random_toggle = wx.CheckBox(self.control_panel, label="Random")
        self.random_toggle.SetValue(True)
        self.random_toggle.Bind(wx.EVT_CHECKBOX, self.on_random_toggle)
        
        self.options_btn = wx.Button(self.control_panel, label="Options")
        
        control_sizer.Add(wx.StaticText(self.control_panel, label="Band:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        control_sizer.Add(self.band_choice, 0, wx.RIGHT, 10)
        control_sizer.Add(wx.StaticText(self.control_panel, label="Content:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        control_sizer.Add(self.type_choice, 0, wx.RIGHT, 10)
        control_sizer.Add(self.random_toggle, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        control_sizer.AddStretchSpacer(1)
        control_sizer.Add(self.options_btn, 0, wx.ALL, 5)
        
        main_panel = wx.Panel(self)
        self.hsk_panel = HSKPanel(main_panel, self.current_band, self.content_type, self.random_mode)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.control_panel, 0, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(main_panel, 1, wx.EXPAND)
        
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.AddStretchSpacer(1)
        panel_sizer.Add(self.hsk_panel, 0, wx.CENTER)
        panel_sizer.AddStretchSpacer(1)
        main_panel.SetSizer(panel_sizer)
        
        self.control_panel.SetSizer(control_sizer)
        self.SetSizer(main_sizer)

        self.options_btn.Bind(wx.EVT_BUTTON, self.on_options)
        self.Center()
        self.Show()

    def on_band_change(self, event):
        self.current_band = int(self.band_choice.GetStringSelection())
        self.hsk_panel.update_content(self.current_band, self.content_type)

    def on_type_change(self, event):
        self.content_type = 'char' if self.type_choice.GetSelection() == 0 else 'vocab'
        self.hsk_panel.update_content(self.current_band, self.content_type)

    def on_random_toggle(self, event):
        self.random_mode = self.random_toggle.GetValue()
        self.hsk_panel.set_random_mode(self.random_mode)

    def on_options(self, event):
        dlg = ConfigDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.SaveConfig():
                self.hsk_panel.reload_config()
        dlg.Destroy()

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()

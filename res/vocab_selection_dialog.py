import wx
import wx.grid
import csv
import os

class VocabSelectionDialog(wx.Dialog):
    def __init__(self, parent, initial_band, initial_content_type):
        super().__init__(parent, title="Select Vocabulary for Study", size=(800, 350),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.selected_vocab = []
        self.data = []
        self.initial_band = initial_band
        self.initial_content_type = initial_content_type
        self.config = {
            'characters': 'simplified',
            'readings': 'pinyin'
        }
        self.load_config()

        self.init_ui()
        self.load_data_for_display()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Controls for band and content type selection shit
        control_panel = wx.Panel(self)
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.band_choice = wx.Choice(control_panel, choices=[str(i) for i in range(1, 7)])
        self.band_choice.SetSelection(self.initial_band - 1)
        self.band_choice.Bind(wx.EVT_CHOICE, self.on_selection_change)

        self.type_choice = wx.Choice(control_panel, choices=['Characters', 'Vocabulary'])
        self.type_choice.SetSelection(0 if self.initial_content_type == 'char' else 1)
        self.type_choice.Bind(wx.EVT_CHOICE, self.on_selection_change)

        control_sizer.Add(wx.StaticText(control_panel, label="Band:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        control_sizer.Add(self.band_choice, 0, wx.RIGHT, 10)
        control_sizer.Add(wx.StaticText(control_panel, label="Content:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        control_sizer.Add(self.type_choice, 0, wx.RIGHT, 10)
        control_panel.SetSizer(control_sizer)
        main_sizer.Add(control_panel, 0, wx.EXPAND | wx.ALL, 5)

        # Grid for displaying vocabulary :^)
        self.grid = wx.grid.Grid(self, -1)
        self.grid.CreateGrid(0, 5)
        self.grid.EnableEditing(False)
        self.grid.SetColLabelValue(0, "")
        self.grid.SetColLabelValue(1, "Simplified")
        self.grid.SetColLabelValue(2, "Traditional")
        self.grid.SetColLabelValue(3, "Reading")
        self.grid.SetColLabelValue(4, "Meaning")

        # Set column sizes
        self.grid.SetColSize(0, 30)
        self.grid.SetColSize(1, 100)
        self.grid.SetColSize(2, 100)
        self.grid.SetColSize(3, 100)
        self.grid.SetColSize(4, 300)

        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_grid_cell_click)

        min_grid_content_height = (self.grid.GetDefaultRowSize() * 5) + self.grid.GetColLabelSize()
        self.grid.SetMinSize(wx.Size(-1, min_grid_content_height))
        main_sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 10)

        # Buttons and what not
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.select_all_btn = wx.Button(self, label="Select All")
        self.deselect_all_btn = wx.Button(self, label="Deselect All")
        ok_button = wx.Button(self, wx.ID_OK, "Start Study")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.select_all_btn.Bind(wx.EVT_BUTTON, self.on_select_all)
        self.deselect_all_btn.Bind(wx.EVT_BUTTON, self.on_deselect_all)

        button_sizer.Add(self.select_all_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.deselect_all_btn, 0, wx.ALL, 5)
        button_sizer.AddStretchSpacer(1)
        button_sizer.Add(ok_button, 0, wx.ALL, 5)
        button_sizer.Add(cancel_button, 0, wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.SetSizer(main_sizer)
        self.Fit() 
        self.SetClientSize(wx.Size(750, 450)) 
        self.CenterOnScreen()

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
            print(f"Error loading config in VocabSelectionDialog: {e}, using defaults")

    def load_data_for_display(self):
        current_band = int(self.band_choice.GetStringSelection())
        current_content_type = 'char' if self.type_choice.GetSelection() == 0 else 'vocab'
        filename = os.path.join('res', f'band{current_band}_{current_content_type}.csv')

        self.data = []
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    self.data.append(row)
            self.populate_grid()
        except FileNotFoundError:
            wx.MessageBox(f"Data file '{filename}' not found!", "Error", wx.OK | wx.ICON_ERROR)
            self.data = []
            self.populate_grid()

    def populate_grid(self):
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())

        self.grid.AppendRows(len(self.data))
        self.checkbox_states = [False] * len(self.data)

        char_col = 0 if self.config['characters'] == 'simplified' else 1
        reading_col = 2 if self.config['readings'] == 'pinyin' else 3

        for i, row_data in enumerate(self.data):
            self.grid.SetCellRenderer(i, 0, wx.grid.GridCellBoolRenderer())
            self.grid.SetCellEditor(i, 0, wx.grid.GridCellBoolEditor())
            self.grid.SetCellValue(i, 0, "1" if self.checkbox_states[i] else "0")

            self.grid.SetCellValue(i, 1, row_data[0])
            self.grid.SetCellValue(i, 2, row_data[1])
            self.grid.SetCellValue(i, 3, row_data[reading_col])
            self.grid.SetCellValue(i, 4, row_data[4])

        self.grid.AutoSizeColumns()
        self.grid.Refresh()

    def on_selection_change(self, event):
        self.load_data_for_display()

    def on_grid_cell_click(self, event):
        col = event.GetCol()
        row = event.GetRow()

        if col == 0:
            self.checkbox_states[row] = not self.checkbox_states[row]
            self.grid.SetCellValue(row, 0, "1" if self.checkbox_states[row] else "0")
            self.grid.Refresh()
        event.Skip()

    def on_select_all(self, event):
        for i in range(len(self.checkbox_states)):
            self.checkbox_states[i] = True
            self.grid.SetCellValue(i, 0, "1")
        self.grid.Refresh()

    def on_deselect_all(self, event):
        for i in range(len(self.checkbox_states)):
            self.checkbox_states[i] = False
            self.grid.SetCellValue(i, 0, "0")
        self.grid.Refresh()

    def GetSelectedVocab(self):
        selected = []
        char_col = 0 if self.config['characters'] == 'simplified' else 1
        reading_col = 2 if self.config['readings'] == 'pinyin' else 3

        for i, is_selected in enumerate(self.checkbox_states):
            if is_selected:
                row_data = self.data[i]
                selected.append((
                    row_data[char_col],
                    row_data[reading_col],
                    row_data[5],
                    row_data[4]
                ))
        return selected

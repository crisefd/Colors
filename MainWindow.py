from gi.repository import Gtk, Gdk, GdkPixbuf, Pango
import random

MARKED = -1
MATCHED = 0
UNMATCHED = 1
UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menu action='GameNew'>
        <menuitem action='Level1' />
        <menuitem action='Level2' />
        <menuitem action='Level3' />
      </menu>
      <separator />
      <menuitem action='LeaveGame' />
      <menuitem action='FileQuit' />
    </menu>
    <menu action='GameMenu'>
      <menuitem action='ChangeBackgroundImage' />
      <menuitem action='ShowScores' />
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='ReadManual'/>
      <menuitem action='About'/>
    </menu>
  </menubar>
</ui>
"""


class EntryDialog(Gtk.MessageDialog):

    def __init__(self, *args, **kwargs):
        if 'default_value' in kwargs:
            default_value = kwargs['default_value']
            del kwargs['default_value']
        else:
            default_value = 'Player'
        super(EntryDialog, self).__init__(*args, **kwargs)
        self.set_title('Input Player Name')
        self.set_size_request(150, 50)
        entry = Gtk.Entry()
        entry.set_alignment(0.5)
        entry.set_text(str(default_value))
        entry.connect("activate",
                      lambda ent, dlg, resp: dlg.response(resp),
                      self, Gtk.ResponseType.OK)
        self.vbox.pack_start(entry, True, True, 0)
        self.vbox.show_all()
        self.entry = entry
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('black'))
        #self.set_opacity(0.0)
        self.show_all()
        self.connect('delete-event', Gtk.main_quit)
        self.res = default_value
        self.run()
        #Gtk.main()

    def set_value(self, text):
        self.entry.set_text(text)

    def run(self):
        result = super(EntryDialog, self).run()
        if result == Gtk.ResponseType.OK:
            text = self.entry.get_text()
            self.destroy()
        else:
            text = None
        self.res = text


class ScoresDialog(Gtk.Window):

    def __init__(self, mainwindow, val):
        super(ScoresDialog, self).__init__(title='Scores')
        self.set_size_request(500, 230)
        self.set_resizable(False)
        treeView = Gtk.TreeView()
        fix = Gtk.Fixed()
        #self.get_content_area().add(treeView)
        self.add(fix)
        background_image = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('Images/BG2.jpg',
                                            510, 480)
        background_image.set_from_pixbuf(pixbuf)
        fix.put(background_image, 0, 0)
        fix.put(treeView, 60, 0)
        levelOneColumn = Gtk.TreeViewColumn()
        levelOneColumn.set_title('Level 1   [name clicks]')
        levelOneNameCell = Gtk.CellRendererText()
        levelOneColumn.pack_start(levelOneNameCell, False)
        treeView.append_column(levelOneColumn)
        levelOneColumn.add_attribute(levelOneNameCell, 'text', 0)

        levelTwoColumn = Gtk.TreeViewColumn()
        levelTwoColumn.set_title('Level 2   [name clicks]')
        levelTwoNameCell = Gtk.CellRendererText()
        levelTwoColumn.pack_start(levelTwoNameCell, False)
        treeView.append_column(levelTwoColumn)
        levelTwoColumn.add_attribute(levelTwoNameCell, 'text', 1)

        levelThreeColumn = Gtk.TreeViewColumn()
        levelThreeColumn.set_title('Level 3   [name clicks]')
        levelThreeNameCell = Gtk.CellRendererText()
        levelThreeColumn.pack_start(levelThreeNameCell, False)
        treeView.append_column(levelThreeColumn)
        levelThreeColumn.add_attribute(levelThreeNameCell, 'text', 2)
        treeView.set_enable_search(False)
        listStore = Gtk.ListStore(str, str, str)
        if val == 0:
            data = self.read_file()
            level_scores = self.get_level_scores(mainwindow, data)
            self.sort_scores(level_scores)
            self.update_data(mainwindow, level_scores, data)
            for item in data:
                listStore.append(item)
            treeView.set_model(listStore)
        if val > 0:
            self.write_file(mainwindow)
            data = self.read_file()
            for item in data:
                listStore.append(item)
            treeView.set_model(listStore)
        self.show_all()
        self.connect('delete-event', self.quit_f)
        #self.run()

    def quit_f(self, var1, var2):
        self.destroy()

    def get_level_scores(self, mainwindow, data):
        level = mainwindow.level_entry.get_text()
        level_scores = []
        for item in data:
            if level == '1':
                level_scores.append(item[0])
            elif level == '2':
                level_scores.append(item[1])
            elif level == '3':
                level_scores.append(item[2])
        return level_scores

    def update_data(self, mainwindow, level_scores, data):
        level = mainwindow.level_entry.get_text()
        for k in range(0, len(data)):
            if level == '1':
                data[k][0] = level_scores[k]
            elif level == '2':
                data[k][1] = level_scores[k]
            elif level == '3':
                data[k][2] = level_scores[k]

    def sort_scores(self, level_scores):
        j = 0
        for i in range(1, len(level_scores)):
            item = level_scores[i]
            tok = item.split(" ")
            score_t = int(tok[1])

            j = i
            while j > 0 and int(level_scores[j - 1].split(" ")[1]) > score_t:
                level_scores[j] = level_scores[j - 1]
                j -= 1
            level_scores[j] = item

    def write_file(self, mainwindow):
        pass

    def find(self, a, col):
        i = 0
        for string in col:
            t = string.split(' ', len(string))
            n = int(t[1])
            if n == a:
                del col[i]
                return string
            i += 1

    def read_file(self):
        myfile = open('Persistance/scores.txt', 'r')
        data = []
        try:
            i = 1
            while i <= 5:
                line = myfile.readline().replace('\n', '')
                tokens = line.split('$', len(line))
                data.append(tokens)
                i += 1
        except IOError:
            print('I/O Error, cannot open file')
        except Exception as ex:
            print(('Unexpected error ', ex))
        finally:
            myfile.close()
        return data


class ManualDialog(Gtk.Dialog):

    def __init__(self, parent):
        super(ManualDialog, self).__init__("About", parent, 0, (Gtk.STOCK_OK,
                         Gtk.ResponseType.OK))
        self.set_size_request(400, 300)
        self.set_resizable(False)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textview.set_sensitive(False)
        self.textview.set_editable(False)
        self.textbuffer.set_text("This is some text inside of a Gtk.TextView.\n"
            + "************************************************************\n, "
            + "*************************************************************")
        scrolledwindow.add(self.textview)
        self.get_content_area().add(scrolledwindow)
        self.show_all()
        self.connect('delete-event', self.quit_f)
        self.run()

    def quit_f(self, widget, par):
        self.destroy()

    def run(self):
        result = super(ManualDialog, self).run()
        if result == Gtk.ResponseType.OK:
            self.destroy()


class AboutDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "About", parent, 0, (Gtk.STOCK_OK,
                         Gtk.ResponseType.OK))
        self.set_default_size(500, 200)
        self.set_resizable(False)
        box = Gtk.HBox()
        im = Gtk.Image()
        im.set_from_file('Images/cube.png')
        label = Gtk.Label('Institution: Universidad del Valle (Colombia)\n\n Dependency: Escuela de Ingenieria de Sistemas y Computacion\n\nAuthor: Cristhian Eduardo Fuertes Daza\n\nDate: July 17 del 2014')
        im.show()
        box.pack_start(im, expand=True, fill=False, padding=10)
        box.pack_start(label, expand=True, fill=False, padding=10)
        self.get_content_area().add(box)
        self.show_all()
        self.connect('delete-event', self.quit_f)
        self.run()
        #Gtk.main()

    def quit_f(self, widget, par):
        self.destroy()

    def run(self):
        result = super(AboutDialog, self).run()
        if result == Gtk.ResponseType.OK:
            self.destroy()


class MainWindow(Gtk.Window):

    def __init__(self):
        super(MainWindow, self).__init__(title='Colors')
        self.num_marked_cells = 1
        self.set_resizable(False)
        self.fix = Gtk.Fixed()
        self.add(self.fix)
        self.dim = 8
        self.background_image = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('Images/BG.jpg',
                                            1280, 960)
        self.background_image.set_from_pixbuf(pixbuf)
        self.fix.put(self.background_image, 0, 0)
        self.built_button_box()
        self.fix.put(self.buttons_box, 0, 685)
        self.built_lateral_grid()
        #self.built_label_grid()
        self.fix.put(self.lateral_grid, 1000, 120)
        #self.fix.put(self.label_grid, 250, 120)
        self.connect('delete-event', Gtk.main_quit)
        self.show_all()
        iconImage = Gtk.Image()
        iconImage.set_from_file('Images/Colors.png')
        pixbufIcon = iconImage.get_pixbuf()
        self.set_icon(pixbufIcon)
        self.built_menu_bar()
        Gtk.main()

    def built_lateral_grid(self):
        self.name_entry = Gtk.Entry()
        self.name_entry.set_alignment(0.5)
        self.name_entry.modify_font(
                            Pango.FontDescription.from_string('Arial Bold 11'))
        self.name_entry.set_opacity(0.7)
        self.name_entry.set_size_request(20, 5)
        self.name_entry.set_editable(False)
        self.name_entry.set_can_focus(False)
        self.name_label = Gtk.Label('Name:')
        self.name_label.modify_fg(Gtk.StateType.NORMAL,
                                    Gdk.color_parse('white'))
        self.name_label.modify_font(
                            Pango.FontDescription.from_string('Arial Bold 11'))
        self.clicks_entry = Gtk.Entry()
        self.clicks_entry.set_alignment(0.5)
        self.clicks_entry.modify_font(
                            Pango.FontDescription.from_string('Arial Bold 11'))
        self.clicks_entry.set_opacity(0.7)
        self.clicks_entry.set_size_request(20, 5)
        self.clicks_entry.set_editable(False)
        self.clicks_entry.set_can_focus(False)
        self.clicks_label = Gtk.Label('Clicks:')
        self.clicks_label.modify_fg(Gtk.StateType.NORMAL,
                                    Gdk.color_parse('white'))
        self.clicks_label.modify_font(
                            Pango.FontDescription.from_string('Arial Bold 11'))
        self.level_entry = Gtk.Entry()
        self.level_entry.set_alignment(0.5)
        self.level_entry.modify_font(
                            Pango.FontDescription.from_string('Arial Bold 11'))
        self.level_entry.set_opacity(0.7)
        self.level_entry.set_size_request(20, 5)
        self.level_entry.set_editable(False)
        self.level_entry.set_can_focus(False)
        self.level_label = Gtk.Label('Level:')
        self.level_label.modify_fg(Gtk.StateType.NORMAL,
                                    Gdk.color_parse('white'))
        self.level_label.modify_font(
                            Pango.FontDescription.from_string('Arial Bold 11'))
        self.lateral_grid = Gtk.Grid()
        self.lateral_grid.set_row_spacing(6)
        self.lateral_grid.set_column_spacing(4)
        self.lateral_grid.set_border_width(5)
        self.lateral_grid.attach(self.name_label, 0, 0, 1, 1)
        self.lateral_grid.attach(self.name_entry, 1, 0, 3, 1)
        self.lateral_grid.attach(self.clicks_label, 0, 1, 1, 1)
        self.lateral_grid.attach(self.clicks_entry, 1, 1, 3, 1)
        self.lateral_grid.attach(self.level_label, 0, 2, 1, 1)
        self.lateral_grid.attach(self.level_entry, 1, 2, 3, 1)

    def built_button_box(self):
        self.buttons_box = Gtk.HBox()
        im1 = Gtk.Image()
        im2 = Gtk.Image()
        im3 = Gtk.Image()
        im4 = Gtk.Image()
        im5 = Gtk.Image()
        im6 = Gtk.Image()
        im1.set_from_file('Images/1.png')
        im2.set_from_file('Images/2.png')
        im3.set_from_file('Images/3.png')
        im4.set_from_file('Images/4.png')
        im5.set_from_file('Images/5.png')
        im6.set_from_file('Images/6.png')
        self.blue_button = Gtk.Button()
        self.blue_button.set_sensitive(False)
        self.blue_button.set_image(im1)
        self.blue_button.set_relief(Gtk.ReliefStyle.NONE)
        self.blue_button.connect('clicked', self.on_button_clicked)
        self.green_button = Gtk.Button()
        self.green_button.set_sensitive(False)
        self.green_button.set_image(im2)
        self.green_button.set_relief(Gtk.ReliefStyle.NONE)
        self.green_button.connect('clicked', self.on_button_clicked)
        self.pink_button = Gtk.Button()
        self.pink_button.set_sensitive(False)
        self.pink_button.set_image(im3)
        self.pink_button.set_relief(Gtk.ReliefStyle.NONE)
        self.pink_button.connect('clicked', self.on_button_clicked)
        self.purple_button = Gtk.Button()
        self.purple_button.set_sensitive(False)
        self.purple_button.set_image(im4)
        self.purple_button.set_relief(Gtk.ReliefStyle.NONE)
        self.purple_button.connect('clicked', self.on_button_clicked)
        self.red_button = Gtk.Button()
        self.red_button.set_sensitive(False)
        self.red_button.set_image(im5)
        self.red_button.set_relief(Gtk.ReliefStyle.NONE)
        self.red_button.connect('clicked', self.on_button_clicked)
        self.yellow_button = Gtk.Button()
        self.yellow_button.set_sensitive(False)
        self.yellow_button.set_image(im6)
        self.yellow_button.set_relief(Gtk.ReliefStyle.NONE)
        self.yellow_button.connect('clicked', self.on_button_clicked)
        self.blue_button.set_size_request(212, 20)
        self.green_button.set_size_request(212, 20)
        self.pink_button.set_size_request(212, 20)
        self.purple_button.set_size_request(212, 20)
        self.red_button.set_size_request(212, 20)
        self.yellow_button.set_size_request(212, 20)
        self.buttons_box.pack_start(self.blue_button, expand=True, fill=False,
                                    padding=0)
        self.buttons_box.pack_start(self.green_button, expand=True, fill=False,
                                    padding=0)
        self.buttons_box.pack_start(self.pink_button, expand=True, fill=False,
                                    padding=0)
        self.buttons_box.pack_start(self.purple_button, expand=True, fill=False,
                                    padding=0)
        self.buttons_box.pack_start(self.red_button, expand=True, fill=False,
                                    padding=0)
        self.buttons_box.pack_start(self.yellow_button, expand=True, fill=False,
                                     padding=0)

    def on_button_clicked(self, button):
        val = str(int(self.clicks_entry.get_text()) + 1)
        self.clicks_entry.set_text(val)
        oldColor = self.get_color(self.label_grid.get_child_at(0, 0))
        if button == self.blue_button:
            newColor = Gdk.color_parse('blue')
            self.change_grid_colors(oldColor, newColor)
        elif button == self.green_button:
            newColor = Gdk.color_parse('green')
            self.change_grid_colors(oldColor, newColor)
        elif button == self.pink_button:
            newColor = Gdk.color_parse('pink')
            self.change_grid_colors(oldColor, newColor)
        elif button == self.purple_button:
            newColor = Gdk.color_parse('purple')
            self.change_grid_colors(oldColor, newColor)
        elif button == self.red_button:
            newColor = Gdk.color_parse('red')
            self.change_grid_colors(oldColor, newColor)
        else:
            newColor = Gdk.color_parse('yellow')
            self.change_grid_colors(oldColor, newColor)

        print(self.num_marked_cells)

        if self.num_marked_cells >= self.dim * self.dim:
            self.show_message_dialog()
            self.on_leave_game(None)

    def built_menu_bar(self):
        action_group = Gtk.ActionGroup("my_actions")
        self.add_file_menu_actions(action_group)
        self.add_game_menu_actions(action_group)
        self.add_about_menu_actions(action_group)
        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)
        menubar = uimanager.get_widget("/MenuBar")
        menubar.set_size_request(1280, 10)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)
        box.show()
        menubar.show()
        self.fix.put(box, 0, 0)

    def add_game_menu_actions(self, action_group):
        action_gamemenu = Gtk.Action("GameMenu", "Game", None, None)
        action_group.add_action(action_gamemenu)
        action_change_background = Gtk.Action("ChangeBackgroundImage",
                                              "Change Background Image", None,
                                              Gtk.STOCK_INDEX)
        #print(action_change_background.get_name())
        action_change_background.connect('activate',
                                self.on_change_background_clicked)
        #print(self.filename)
        action_show_scores = Gtk.Action("ShowScores", "Show Scores",
                                        None, None)
        action_show_scores.connect('activate', self.on_show_scores_dialog)
        action_group.add_action(action_change_background)
        action_group.add_action(action_show_scores)

    def add_about_menu_actions(self, action_group):
        action_helpmenu = Gtk.Action("HelpMenu", "Help", None, None)
        action_group.add_action(action_helpmenu)
        action_show_instructions = Gtk.Action("ReadManual", "Read Manual", None,
                                                Gtk.STOCK_DIALOG_INFO)
        action_show_instructions.connect('activate', self.on_show_manual_dialog)
        action_group.add_action(action_show_instructions)
        action_show_about = Gtk.Action("About", "About", None, Gtk.STOCK_ABOUT)
        action_show_about.connect('activate', self.on_show_about_dialog)
        action_group.add_action(action_show_about)

    def on_show_about_dialog(self, widget):
        AboutDialog(self)

    def on_show_manual_dialog(self, widget):
        ManualDialog(self)
        pass

    def add_file_menu_actions(self, action_group):
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)

        action_filenewmenu = Gtk.Action("GameNew", "New", None, Gtk.STOCK_NEW)
        action_group.add_action(action_filenewmenu)

        action_new = Gtk.Action("Level1", "Level 1 8x8",
                            "Creates a new game with a 8x8 grid",
                             None)
        action_new.connect('activate', self.on_menu_file_new_generic)
        action_group.add_action_with_accel(action_new, None)

        action_group.add_actions([
            ("Level2", None, "Level 2 10x10", None,
                    "Creates a new game with a 10x10 grid",
             self.on_menu_file_new_generic),
            ("Level3", None, "Level 3 12x12", None,
                    "Creates a new game with a 12x12 grid",
             self.on_menu_file_new_generic),
        ])
        action_leave_game = Gtk.Action("LeaveGame", "Leave Game", None,
                                        Gtk.STOCK_CANCEL)
        action_leave_game.connect('activate', self.on_leave_game)
        action_group.add_action(action_leave_game)
        action_filequit = Gtk.Action("FileQuit", "Exit", None, Gtk.STOCK_QUIT)
        action_filequit.connect('activate', Gtk.main_quit)
        action_group.add_action(action_filequit)

    def on_leave_game(self, widget):
        self.blue_button.set_sensitive(False)
        self.green_button.set_sensitive(False)
        self.pink_button.set_sensitive(False)
        self.purple_button.set_sensitive(False)
        self.red_button.set_sensitive(False)
        self.yellow_button.set_sensitive(False)
        self.fix.remove(self.label_grid)
        self.name_entry.set_text('')
        self.clicks_entry.set_text('')
        self.level_entry.set_text('')
        self.dim = 0
        self.level = 0
        self.show_all()

    def create_ui_manager(self):
        uimanager = Gtk.UIManager()
        # Throws exception if something went wrong
        try:
            uimanager.add_ui_from_string(UI_INFO)
        except Exception as ex:
            print(('Error, ', ex))
            Gtk.main_quit()
        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager

    def on_show_scores_dialog(self, widget):
        ScoresDialog(self, 0)

    def on_menu_file_new_generic(self, widget):
        ed = EntryDialog(self, 0, Gtk.MessageType.OTHER,
                            Gtk.ButtonsType.OK_CANCEL, None)
        if ed.res is None:
            ed.destroy()
        else:
            self.name_entry.set_text(ed.res)
            self.clicks_entry.set_text('0')
            widget_name = widget.get_name()
            self.level = 0
            if widget_name == 'Level1':
                self.level = 1
                self.dim = 8
            elif widget_name == 'Level2':
                self.level = 2
                self.dim = 10
            else:
                self.level = 3
                self.dim = 12
            self.level_entry.set_text(str(self.level))
            self.built_label_grid()
            self.fix.put(self.label_grid, 250, 120)
            self.show_all()
            self.blue_button.set_sensitive(True)
            self.green_button.set_sensitive(True)
            self.pink_button.set_sensitive(True)
            self.purple_button.set_sensitive(True)
            self.red_button.set_sensitive(True)
            self.yellow_button.set_sensitive(True)

    def built_label_grid(self):
        self.label_grid = Gtk.Grid()
        #self.button_grid.set_size_request(10 * dim, 10 * dim)
        self.label_grid.set_row_spacing(10)
        self.label_grid.set_column_spacing(10)
        colors = ['blue', 'green', 'pink', 'purple', 'red', 'yellow']
        for i in range(0, self.dim):
            for j in range(0, self.dim):
                pos = random.randint(0, 5)
                label = Gtk.Label()

                label.modify_bg(Gtk.StateType.NORMAL,
                                                Gdk.color_parse(colors[pos]))
                label.modify_fg(Gtk.StateType.NORMAL,
                                                Gdk.color_parse(colors[pos]))
                label.set_size_request(30, 30)
                label.set_opacity(0.7)
                self.label_grid.attach(label, j, i, 1, 1)
        #print(self.label_grid.get_child_at(0,0).get_style().bg)

    def get_color(self, widget):
        return widget.get_style_context().get_background_color(
            Gtk.StateType.NORMAL).to_color()

    def on_change_background_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose an image", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)
        filename = ''
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            #print("Open clicked")
            filename = dialog.get_filename()
        #elif response == Gtk.ResponseType.CANCEL:
         #   print("Cancel clicked")
        dialog.destroy()
        #self.fix.remove(self.background_image)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename,
                                            1280, 960)
        self.background_image.set_from_pixbuf(pixbuf)
        #self.background_image.set_size_request(1280, 960)
        #self.fix.put(self.background_image, 0, 0)
        self.show_all()

    def add_filters(self, dialog):
        myfilter = Gtk.FileFilter()
        myfilter.set_name("Image files")
        myfilter.add_mime_type("image/png")
        myfilter.add_mime_type("image/jpg")
        myfilter.add_mime_type("image/gif")
        myfilter.add_mime_type("image/jpeg")
        dialog.add_filter(myfilter)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def is_valid(self, row, column):
        try:
            if row < 0 or column < 0:
                return False
            if row >= self.dim or column >= self.dim:
                return False
            elif self.num_matrix[row][column] == MATCHED:
                return True
            else:
                return False
        except IndexError:
            return False

    def print_matrix(self, M):
        s = ''
        print('================')
        for i in range(0, len(M)):
            for j in range(0, len(M[0])):
                s += str(M[i][j]) + ','
            s += '\n'
        print(s)

    def find_matching_color_cells(self, color):
        self.num_matrix = []
        for i in range(0, self.dim):
            self.num_matrix.append([0] * self.dim)
            for j in range(0, self.dim):
                label = self.label_grid.get_child_at(j, i)
                if i == 0 and j == 0:
                    self.num_matrix[0][0] = MARKED
                elif color == self.get_color(label):
                    self.num_matrix[i][j] = MATCHED
                else:
                    self.num_matrix[i][j] = UNMATCHED

    def mark_cells(self, row, col):
        if self.num_matrix[row][col] == MARKED:
            self.num_marked_cells += 1
            if self.is_valid(row - 1, col):
                #print(("up from row = %d, col= %d" %(row, col)))
                self.num_matrix[row - 1][col] = MARKED
                self.mark_cells(row - 1, col)

            if self.is_valid(row, col - 1):
                #print(("left from row = %d, col= %d" %(row, col)))
                self.num_matrix[row][col - 1] = MARKED
                self.mark_cells(row, col - 1)

            if self.is_valid(row + 1, col):
                #print(("down from row = %d, col= %d" %(row, col)))
                self.num_matrix[row + 1][col] = MARKED
                self.mark_cells(row + 1, col)

            if self.is_valid(row, col + 1):
                #print(("up from row = %d, col= %d" %(row, col)))
                self.num_matrix[row][col + 1] = MARKED
                self.mark_cells(row, col + 1)

    def change_grid_colors(self, oldColor, newColor):
        self.find_matching_color_cells(oldColor)
        #print("BEFORE MARKED")
       # self.print_matrix(self.num_matrix)
        self.num_marked_cells = 1
        self.mark_cells(0, 0)
       # print("AFTER MARKED")
        #self.print_matrix(self.num_matrix)
        for i in range(0, self.dim):
            for j in range(0, self.dim):
                if self.num_matrix[i][j] == MARKED:
                    self.label_grid.get_child_at(j, i).modify_bg(
                                                           Gtk.StateType.NORMAL,
                                                           newColor)

    def show_message_dialog(self):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "CONGRATULATIONS !")
        dialog.format_secondary_text(
            "You won. Number of clicks: " + self.clicks_entry.get_text())
        dialog.run()
        #print("INFO dialog closed")
        dialog.destroy()

MainWindow()
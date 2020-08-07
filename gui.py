from tkinter import *
from abc import ABC, abstractmethod


class GameGUI(ABC):
    def __init__(self, game):
        self.game = game

        self.window = Tk(className=str(self.game))

        self.command_variable = StringVar()
        self.command_variable.trace_add("write", self.filter_available_commands)

        self.available_commands = []
        self.filtered_commands = []

        self.frm_out = Frame(self.window)
        self.frm_out.pack(side=LEFT, fill=BOTH, expand=True)

        self.frm_in = Frame(self.window, relief=GROOVE, borderwidth=5)
        self.frm_in.pack(fill=Y, side=RIGHT)
        self.frm_in.bind_all("<Return>", self.execute_command)

        self.ent_command = self.create_command_entry()
        self.frm_available_commands = self.create_available_commands()
        self.update_available_commands()
        self.board = self.create_board()
        self.update_board()

    @abstractmethod
    def create_board(self, *args):
        pass

    @abstractmethod
    def update_board(self, *args):
        pass

    def create_command_entry(self, *args):
        lbl_command = Label(self.frm_in, text="Enter Command:")
        ent_command = Entry(self.frm_in, textvariable=self.command_variable)
        frm_buttons = Frame(self.frm_in)
        btn_execute_command = Button(frm_buttons, text="Execute Command", command=self.execute_command)
        btn_clr_command = EntryOption(frm_buttons, ent_command, "", "Clear Command").button

        lbl_command.grid(row=0, column=0)
        ent_command.grid(row=1, column=0)
        frm_buttons.grid(row=2, column=0)
        btn_execute_command.grid(row=0, column=1)
        btn_clr_command.grid(row=0, column=0)

        return ent_command

    def create_available_commands(self, *args):
        lbl_available_commands = Label(self.frm_in, text="Available Commands:")
        frm_available_commands = Frame(self.frm_in)
        lbl_available_commands.grid(row=3, column=0)
        frm_available_commands.grid(row=2, column=0)

        return frm_available_commands

    def update_available_commands(self, *args):
        self.available_commands = [(self.game.move_to_string(move), move) for move in self.game.get_legal_moves()]
        self.filter_available_commands()

    def filter_available_commands(self, *args):
        self.filtered_commands = []
        for command_string, command in self.available_commands:
            if self.command_variable.get() in command_string:
                self.filtered_commands.append((command_string, command))

        frm_new = Frame(self.frm_in)
        frm_old = self.frm_available_commands
        [EntryOption(frm_new, self.ent_command, command_string).button.pack()
            for command_string, command in self.filtered_commands]
        self.frm_available_commands = frm_new
        self.frm_available_commands.grid(row=4, column=0)
        frm_old.destroy()

    def execute_command(self, *args):
        if self.filtered_commands:
            self.game.execute_move(self.filtered_commands[0][1])
            self.ent_command.delete(0, END)
            self.update_available_commands()
            self.update_board()


class EntryOption:
    def __init__(self, master, entry, text, label=None):
        self.entry = entry
        self.text = text
        if label:
            self.label = label
        else:
            self.label = text
        self.button = Button(master, text=self.label, command=self.command)

    def command(self):
        self.entry.delete(0, END)
        self.entry.insert(0, self.text)

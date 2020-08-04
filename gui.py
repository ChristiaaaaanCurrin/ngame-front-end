from tkinter import *
from abc import ABC, abstractmethod
from tic_tac_toe import TicTacToe


class GameGUI(ABC):
    def __init__(self, game):
        self.game = game

        self.window = Tk(className=str(self.game))

        self.command_variable = StringVar()
        self.command_variable.trace_add("write", self.update_available_commands)
        self.available_commands = []

        self.frm_out = Frame(self.window)
        self.frm_in = Frame(self.window)
        self.frm_out.grid(row=0, column=0)
        self.frm_in.grid(row=0, column=1)

        self.lbl_command = Label(self.frm_in, text="Enter Command:")
        self.ent_command = Entry(self.frm_in, textvariable=self.command_variable)
        self.btn_execute_command = Button(self.frm_in, text="Execute Command", command=self.execute_command)
        self.lbl_available_commands = Label(self.frm_in, text="Available Commands:")
        self.frm_available_commands = Frame(self.frm_in)

        self.update_available_commands()

        self.lbl_command.grid(row=0, column=0)
        self.ent_command.grid(row=1, column=0)
        self.btn_execute_command.grid(row=1, column=1)
        self.lbl_available_commands.grid(row=2, column=0)
        self.frm_available_commands.grid(row=3, column=0)

    def update_available_commands(self, *args):
        self.available_commands = []
        for command in self.game.get_legal_moves():
            command_string = self.game.move_to_string(command)
            if self.command_variable.get() in command_string:
                self.available_commands.append((command_string, command))
        self.frm_available_commands.destroy()
        self.frm_available_commands = Frame(self.window)
        [EntryOption(self.frm_available_commands, self.ent_command, command_string).button.pack()
         for command_string, command in self.available_commands]
        self.frm_available_commands.grid(row=3, column=0)

    def execute_command(self, *args):
        if self.available_commands:
            self.game.execute_move(self.available_commands[0][1])
        self.ent_command.delete(0, END)
        self.available_commands = [(self.game.move_to_string(move), move) for move in self.game.get_legal_moves()]


class EntryOption:
    def __init__(self, master, entry, text):
        self.entry = entry
        self.text = text
        self.button = Button(master, text=self.text, command=self.command)

    def command(self):
        self.entry.delete(0, END)
        self.entry.insert(0, self.text)


if __name__ == "__main__":

    test_game = TicTacToe()
    x = GameGUI(test_game)
    x.window.mainloop()

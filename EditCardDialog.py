__author__ = "Rick Myers"

import tkinter as tk
import tkinter.scrolledtext as tkscrolled
import tkinter.messagebox as mbox
import copy
from GiftCard import GiftCard
from datetime import date


class EditCardDialog(tk.Toplevel):

    """
    The is a window that can be used to edit a gift card's balance and view gift card
    information. It displays the card name, balance, starting balance, and any history
    of transactions.
    """

    def __init__(self, parent, card, title=None):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.card = card
        self.result = None
        self.new_balance = copy.deepcopy(self.card.balance)
        self.new_history = copy.deepcopy(self.card.history)

        main_frame = tk.Frame(self)

        # Top frame for label and card name
        label_frame = tk.Frame(self)
        label_frame.grid(sticky=tk.NSEW)

        top_label_var = tk.StringVar(main_frame)
        top_label = tk.Label(label_frame, textvar=top_label_var, fg="black", bg="white", font=('Terminal', 20))
        top_label.grid(row=0, column=0, pady=5, sticky=tk.NSEW)
        top_label_var.set("Gift Card Ledger")

        card_label_var = tk.StringVar(main_frame)
        card_label = tk.Label(label_frame, textvar=card_label_var, fg="black", bg="white", font=('Terminal', 20))
        card_label.grid(row=1, column=0, pady=5, sticky=tk.N)
        card_label_var.set(self.card.name)

        # Middle frame for balance information
        balance_frame = tk.Frame(self)
        balance_frame.grid(sticky=tk.NSEW)

        tk.Label(balance_frame, text="Current Balance: ", anchor=tk.W).grid(sticky=tk.NW)
        self.balance_entry = tk.Entry(balance_frame)
        self.balance_entry.bind("<Return>", self._update_balance)
        self.balance_entry.grid(row=0, column=2, sticky=tk.NE)
        tk.Label(balance_frame, text="Starting Balance: ", anchor=tk.W).grid(row=1, sticky=tk.NW)
        self.balance_label = tk.Label(balance_frame, text=self.card.formatted_balance(),
                                      anchor=tk.W)
        self.balance_label.grid(row=0, column=1, sticky=tk.N)
        tk.Label(balance_frame, text=GiftCard.format_balance(self.card.starting_balance),
                 anchor=tk.W).grid(row=1, column=1, sticky=tk.N)

        # Bottom frame to hold card history
        history_frame = tk.Frame(self)
        history_frame.grid(sticky=tk.NSEW)

        self.history_txt = tkscrolled.ScrolledText(history_frame, width=24, height=10)
        self.history_txt.insert(1.0, self.card.history)
        self.history_txt.config(state=tk.DISABLED)

        self.history_txt.grid(sticky=tk.NSEW)

        # Main frame setup
        main_frame.grid(sticky=tk.NSEW)
        main_frame.columnconfigure(0, weight=1)

        # Button frame setup
        box = tk.Frame(self)

        w = tk.Button(box, text="Save", width=10, command=self.save, default=tk.ACTIVE)
        w.grid(padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.grid(row=0, column=1, padx=5, pady=5)

        self.bind("<Escape>", self.cancel)

        box.grid()

        self.grab_set()
        self.initial_focus = self.balance_entry
        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

        self.initial_focus.focus_set()

    def _update_balance(self, event=None):
        """
        Update the current displayed balance and history for the card within the window.
        The entries will not be saved until the user clicks save. The changes are purely
        visual.

        :param event: The event triggered by pressing <Return> in the edit balance entry.
        """
        # Validate submitted input
        update = self.validate()
        if not update:
            self.initial_focus.focus_set()
            return
        # Deduct spent from current balance.
        self.new_balance -= update
        f_balance = GiftCard.format_balance(self.new_balance)
        self.balance_label.configure(text=f_balance)
        self.balance_entry.delete(0, tk.END)
        # Add updated history to card
        new_history = str(date.today()) + " -> {}".format(f_balance + "\n")
        self.new_history += new_history
        self.history_txt.config(state=tk.NORMAL)
        self.history_txt.delete(1.0, tk.END)
        self.history_txt.insert(1.0, self.new_history)
        self.history_txt.config(state=tk.DISABLED)

    def save(self, event=None):
        """
        Insure the data entered is valid before saving to db and returning to previous windows.

        :param event: (tkinter.Event) The event triggered by clicking the save button.
        """
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        """
        Set the focus back to the parent window and destroys self.
        :param event: (tkinter.Event) The event triggered by clicking the cancel button.
        """
        self.parent.focus_set()
        self.destroy()

    def validate(self):
        """
        Insure that the data entered in balance entry is a float. The balance
        entered can be positive or negative.

        :return: (bool) False if data entered is valid, (int) new balance otherwise.
        """
        try:
            balance = float(self.balance_entry.get())
        except ValueError:
            mbox.showerror("Error", "Invalid balance.")
            return False
        return balance

    def apply(self):
        """
        Save validated results to self.result so that data can be retrieved by
        parent window.
        :return: (tuple) containing the new balance and any new history that
        needs to be saved to the DB and updated on the main window.
        """
        self.result = (self.new_balance, self.new_history)

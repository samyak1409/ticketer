"""
Problem Statement:
Remember: Please use OOPS principle while coming up with the solution for the problem.

Please write a program to build ticketing software for a Zoo. It should have following feature:

1. When the guests arrive at the entrance gate, the person at the ticketing counter should input the number of guests
and age of each guest. The pricing depend on the age as follows:

If age <= 2 years, entrance price is INR 0.
If age > 2 and < 18 years, entrance price is INR 100.
If age >= 18 and < 60 years, entrance price is INR 500.
If age >= 60 years, entrance price is INR 300.

Your software should issue an entrance ticket and display the total charges on the ticket based on the number of guests
and their age.

2. Before entering the Zoo, the security personnel should be able to validate the ticket i.e. they should be able to see
the guests and their age associated with the ticket and manually verify the guests who are trying to enter the Zoo.

Your software should be able to take an issued ticket and display ticket details (a line for each guest on the ticket -
person, age) so security personnel can confirm the guests before letting them enter the Zoo. Ex: If a ticket was issued
for 2 guest (age 23 and 25), it should display:

Guest 1 (age: 23)
Guest 2 (age: 25)

2.1 Bonus: Your software should display a warning in case the ticket has already been used in the past to enter into the
Zoo.
"""


# Imports:
from pickle import dump, load
from os import remove
from sqlite3 import connect
from tkinter.filedialog import askopenfilename


# Class:
class Ticket:

    # Connecting to DB:
    conn = connect('DB.sqlite')
    cur = conn.cursor()

    # Creating table if not exists:
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS "Records" 
                    (
                    "id"	INTEGER NOT NULL,
                    "used"	INTEGER NOT NULL,
                    PRIMARY KEY("id")
                    );
    ''')
    conn.commit()

    # Getting ticket number from DB:
    cur.execute('SELECT max(id) FROM Records')
    last_num = cur.fetchone()[0]  # last ticket number
    # print(last_num)  # debug
    if last_num:
        number = last_num + 1  # next ticket number to be
    else:  # first ticket
        number = 1

    def __init__(self):
        """Feature 1"""

        # Input number of guests with exception handling:
        while True:
            try:
                self.no_of_guests = int(input('Number of Guests: ').strip())
                if self.no_of_guests < 1:
                    raise ValueError
            except ValueError:
                print('Please enter a valid number.')
            else:
                # print(self.no_of_guests)  # debug
                break

        self.ages = []  # list of age of guests
        self.prices = []  # list of entrance price of guests
        self.total = 0  # total charges

        # Input age of guests and calculate charges:
        for i in range(1, self.no_of_guests+1):

            # Input age of guests with exception handling:
            while True:
                try:
                    age = int(input(f'Age of Guest {i}: ').strip())
                    if age < 0:
                        raise ValueError
                except ValueError:
                    print('Please enter a valid number.')
                else:
                    self.ages.append(age)
                    break

            # Pricing Calc:
            if age <= 2:
                price = 0
            elif 2 < age < 18:
                price = 100
            elif 18 <= age < 60:
                price = 500
            else:  # (if age >= 60)
                price = 300

            self.prices.append(price)
            self.total += price

        # print(self.ages)  # debug
        # print(self.prices)  # debug
        # print(self.total)  # debug

        self.id = Ticket.number  # ticket id
        Ticket.number += 1  # inc next ticket number to be

        # Update DB with next ticket number and Insert current ticket info:
        Ticket.cur.execute('INSERT INTO Records VALUES (?, ?)', (self.id, 0))  # id : used :: Ticket.id : It's usage info (0 / 1)
        Ticket.conn.commit()

        print('\nTicket Number:', self.id)
        print(f'Total Charges: INR {self.total}')

    def display(self):
        """Feature 2 and 2.1"""

        # Check if the ticket is already used:
        Ticket.cur.execute('SELECT used FROM Records WHERE id = ?', (self.id,))
        used = Ticket.cur.fetchone()[0]
        # print(used)  # debug

        if not used:  # valid ticket

            print('Ticket Number:', self.id)
            for i in range(self.no_of_guests):
                print(f'Guest {i+1} (age: {self.ages[i]})')

            # Update DB with the ticket used info:
            Ticket.cur.execute('UPDATE Records SET used = ? WHERE id = ?', (1, self.id))
            Ticket.conn.commit()

            return 1

        else:  # already used ticket
            print('WARNING!! This ticket is a copy of an already used ticket.')
            return 0


# Main:
if __name__ == '__main__':

    print('\nWELCOME TO THE ZOO!')

    while True:  # ticket counter's always opened

        choice = input(f"\nEnter '0' to Issue or '1' to Display a ticket: ").strip()
        if choice not in {'0', '1'}:  # invalid choice
            print('Exiting...')
            Ticket.conn.close()  # disconnecting from DB
            exit()

        if choice == '0':  # issue ticket

            print('\n<TICKET COUNTER>\n')  # spacing

            ticket = Ticket()

            # Storing the Ticket object to a file:
            file = f'Tickets\\Ticket {ticket.id}.txt'
            with open(file=file, mode='xb') as t:
                dump(obj=ticket, file=t)

            print(f'Congratulations! Your ticket has been saved to "{file}".')

        else:  # display ticket

            file = askopenfilename(parent=None, title='Open your ticket', initialdir='Tickets', filetypes=[('Only txt format is supported.', '.txt')])
            if not file:
                print('Ticket not found.')
                continue

            # Loading the Ticket object from file:
            with open(file=file, mode='rb') as t:
                ticket = load(file=t)

            print('\n<TICKET CHECK>\n')
            valid = ticket.display()
            if valid:
                print('\nGuest\'s Entry Done, Destroying Ticket...')
            else:
                print('\nGuest\'s Entry Prohibited, Destroying Ticket...')
            remove(file)

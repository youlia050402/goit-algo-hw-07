from collections import UserDict
from datetime import date, datetime, timedelta
from functools import wraps



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
     pass

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
                 super().__init__(value)
        else:
             raise ValueError("Номер телефону повинен містити 10 цифр")

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")  
            self.value = value
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


        
    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)


    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None  


    def add_phone(self, phone):
         phone = Phone(phone)
         self.phones.append(phone)
         return f"Contact {self.name} added with phone number {phone.value}."
    

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
            return f"Contact {self.name.value} removed with phone number {phone}."
        return f"Phone number {phone} not found."

    

    def edit_phone(self, old_phone, new_phone):
       phone_obj = self.find_phone(old_phone)
       if not phone_obj:
            raise ValueError("Старий номер телефону не знайдено")

       new_phone_obj = Phone(new_phone)
       index = self.phones.index(phone_obj)
       self.phones[index] = new_phone_obj
    

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday  = Birthday(birthday)
        return f"День народження {self.birthday.value.strftime('%d.%m.%Y')} додано для контакту {self.name.value}."


  
    def __str__(self):
        phones_str = '; '.join(phone.value for phone in self.phones)
        result = f"Contact name: {self.name.value}, phones: {phones_str}"
        return result


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record


    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        return self.data.get(name)


    def adjust_for_weekend(self, birthday):
            if birthday.weekday() >= 5:
                return self.find_next_weekday(birthday, 0)
            return birthday
    
    def get_upcoming_birthdays(self, users, days=7):
        upcoming_birthdays = []
        today = date.today()
    
        for user in users:
            birthday_this_year = user["birthday"].replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            if 0 <= (birthday_this_year - today).days <= days:
                congratulation_date = self.adjust_for_weekend(birthday_this_year)
                congratulation_date_str = self.date_to_string(congratulation_date)
                upcoming_birthdays.append({"name": user["name"], "congratulation_date": congratulation_date_str})
        return upcoming_birthdays

    def __str__(self):
            return '\n'.join(str(record) for record in self.data.values())

def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e) if str(e) else "Помилка: введено некоректне значення. Будь ласка, спробуйте ще раз."
        except IndexError:
            return "Помилка: недостатньо аргументів. Будь ласка, перевірте введені дані."
        except KeyError:
            return "Помилка: контакт не знайдено. Будь ласка, перевірте ім'я контакту."
        except AttributeError:
            return "Помилка: у цього контакту відсутня дата народження або контакт не знайдено."
    return inner


def parse_input(user_input):
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    return cmd.strip().lower(), args
  


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return f"Контакт {name} оновлено з новим номером телефону {phone}."
    else:
        new_record = Record(name)
        new_record.add_phone(phone)
        book.add_record(new_record)
        return f"Контакт {name} додано з номером телефону {phone}."

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Контакт {name} оновлено з новим номером телефону {new_phone}."
    else:
        return f"Контакт {name} не знайдено."

@input_error
def remove_contact(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        book.delete(name)
        return f"Контакт {name} видалено."
    else:
        return f"Контакт {name} не знайдено."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        phones = ', '.join(phone.value for phone in record.phones)
        return f"Номер(и) телефону для {name}: {phones}."
    else:
        return f"Контакт {name} не знайдено."


@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "Немає доступних контактів."
    return str(book)

@input_error
def add_birthday(args, book: AddressBook):
    name = args[0]
    birthday_str = args[1]
    record = book.find(name)
    if record:
        return f"День народження {birthday_str} додано для контакту {name}."
    else:
        new_record = Record(name)
        new_record.add_birthday(birthday_str)
        book.add_record(new_record)
        return f"Контакт {name} додано з днем народження {birthday_str}."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return f"Контакт {name} не знайдено."
    if not record.birthday:
        return f"У контакта {name} не вказано дату народження."
    birthday_str = record.birthday.value.strftime('%d.%m.%Y')
    return f"{name} має день народження {birthday_str}."
    

@input_error
def birthdays(book: AddressBook):
    birthdays = book.get_upcoming_birthdays(days=int())
    if not birthdays:
        return "Немає майбутніх днів народження протягом 7 днів."
    return "\n".join([f"{bd['name']}: {bd['birthday']}" for bd in birthdays])

def main():
    contacts = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))    
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(args, contacts))
        elif command == "remove":
            print(remove_contact(args, contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show_birthdays":
            print(show-birthdays(args, contacts))
        elif command == "birthdays":
            print(birthdays(contacts))
        else:
            print("Invalid command.")

            
if __name__ == "__main__":
    main()
    
    





from datetime import datetime
from collections import UserDict
import re
import pickle

class Field:
    
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self._validate(new_value)
        self.__value = new_value

    def _validate(self, value):
        pass

    def __str__(self):
        return str(self.__value)

class Name(Field):
    """class for validate name field"""

    def _validate(self, value):
        name_pattern = re.compile(r'^[a-zA-Z0-9а-яА-Я\s]+$')

        if len(value) < 1 or not name_pattern.match(value):
            raise ValueError("Invalid name format")
        
        return f'{value} is a valid name'
        
class Phone(Field):
    """class for validate phone field"""

    def _validate(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits")
        
        return f'{value} is valid phone number'

class Birthday(Field):
    """class for validating birthday field"""

    def _validate(self, value):
        try:
            day, month, year = map(int, value.split('-'))

            if 1 <= day <= 31 and 1 <= month <= 12 and len(str(year)) == 4:

                return f'{value} is valid birthday'
            else:
                raise ValueError('Invalid date: {value}. The date is not correct.')
        except ValueError:
            raise ValueError('Incorrect date format (must be in dd-mm-yyyy)')

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        return f'Number phone {phone} has been add'
    
    def update_birthday(self, new_birthday):
        if self.birthday is not None:
            self.birthday.value = new_birthday
        else:
            self.birthday = Birthday(new_birthday)

    def remove_phone(self, phone):
        tel = Phone(phone)
        if tel.value in [item.value for item in self.phones]:
            self.phones = [item for item in self.phones if tel.value != item.value]
            return f'Number phone {phone} has been removed from contact {self.name.value}.'
        else:
            return f'Phone number {phone} not found in contact {self.name.value}.'

    def edit_phone(self, phone_old, phone_new):
        tel_new = Phone(phone_new)
        for item in self.phones:
            if phone_old == item.value:
                idx = self.phones.index(item)
                self.phones.remove(item)
                self.phones.insert(idx, tel_new)
                return f'Number phone {phone_old} has been changed to {tel_new.value}'
        raise ValueError("Phone number not found for changing")

    def find_phone(self, phone):
        tel = Phone(phone)
        return next((item for item in self.phones if tel.value == item.value), None)

    def days_to_birthday(self):
        today = datetime.now()

        if self.birthday is not None and self.birthday.value is not None:
            birth_day = self.birthday.value
            birth_day = datetime.strptime(birth_day, "%d-%m-%Y")

            next_birthday = datetime(today.year, birth_day.month, birth_day.day)

            if today > next_birthday:
                next_birthday = datetime(today.year + 1, birth_day.month, birth_day.day)

            days_until_birthday = (next_birthday - today).days

            return days_until_birthday
        else:
            raise ValueError('Birthday is not set')
        
    def to_dict(self):
        return {
            'name': self.name.value,
            'phones': [phone.value for phone in self.phones],
            'birthday': self.birthday.value if (self.birthday and hasattr(self.birthday, 'value')) else None
        }

    @classmethod
    def from_dict(cls, data):
        record = cls(name=data['name'], birthday=data['birthday'])
        for phone in data['phones']:
            record.add_phone(phone)
        return record
            
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def add_record(self, obj):
        key = str(obj.name)
        if key in self.data:
            existing_record = self.data[key]
            for phone in obj.phones:
                if phone not in existing_record.phones:
                    existing_record.phones.append(phone)
            if obj.birthday:
                existing_record.birthday = obj.birthday
            print(f"Information added to existing contact: {key}")
        else:
            self.data[key] = obj

    def find(self, name):
        for record in self.data.values():
            if name.lower() == record.name.value.lower():
                return record
        return None
    
    def clear_all_contacts(self):
        yes_no = input('Are you sure you want to delete all users? (y/n) ').lower().strip()
        if yes_no == 'y':
            self.data.clear()
            print("All contacts cleared.")
        else:
             print('Removal canceled')

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f'{name} not found')

    def iterator(self, n=4):
        for i in range(0, len(self.data), n):
            yield list(self.data.values())[i:i + n]

    def save_to_disk(self, filename):
        while not filename.strip():
            filename = input("Enter a valid filename: ").strip()

        try:
            with open(filename, 'wb+') as file:
                data = [record.to_dict() for record in self.data.values()]
                pickle.dump(data, file)
                print(f"Address book saved to {filename}")
        except FileNotFoundError:
            print(f"Error: The specified directory or file '{filename}' does not exist.")
        except Exception as e:
            print(f"Error saving data to '{filename}': {str(e)}")

    def load_from_disk(self, filename):
        while not filename.strip():
            filename = input("Enter a valid filename: ").strip()
        try:
            with open(filename, 'rb+') as file:
                print(f"\nReading data from {filename}")
                data = pickle.load(file)
                self.data.clear()
                for record_data in data:
                    record = Record.from_dict(record_data)
                    self.data[str(record.name)] = record
                print(f"\nAddress book loaded from {filename}")
        except FileNotFoundError:
            print("File not found. Creating a new address book.")
        except Exception as e:
            print(f"Error loading data: {str(e)}")

    def search_contacts(self, query):
        results = []
        query = query.lower()

        for record in self.data.values():
            if (
                query in record.name.value.lower() or
                any(query in phone.value for phone in record.phones)
            ):
                results.append(record)

        return results
    

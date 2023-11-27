from classes import *

address_book = AddressBook()

# Decorator for handling input errors
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name"
        except ValueError as ve:
            return f"ValueError: {str(ve)}"
        except IndexError:
            return "Invalid command format"
        except Exception as e:
            return f"Error: {str(e)}"
    return wrapper

# Function to greet the user
def hello():
    return "Welcome to Your Address Book!\nType 'help' to see available commands and instructions."
    
# Function to get help   
def help():
    return """Please enter the command in accordance with the described capabilities (left column), for the specified type (right column).\n
    Here are some things you can do:\n
        'add <name_contact> <phone> <birthday>'           - Add a new contact with an optional birthday.
        'add <name_contact> <another_phone>'              - Add an additional phone number to an existing contact.
        'birthday <name_contact> <new_birthday_date>'     - Add or update the birthday of an existing contact.
        'change <name_contact> <old_phone> <new_phone>'   - Change an existing phone number of a contact.
        'search'                                          - Search for contacts by name or phone number that match the entered string.
        'when <name_contact>'                             - Show the number of days until the birthday for a contact.
        'phone <name_contact>'                            - Show all phone numbers for a contact.
        'show all'                                        - Display all contacts.
        'remove <name_contact> <phone_number>'            - Remove a phone number from an existing contact.
        'delete <name_contact>'                           - Delete an entire contact.
        'save'                                            - Save the address book to a file.
        'load'                                            - Load the address book from a file.
        'exit' or 'close' or 'good bye'                   - Exit the program.
        'clear all'                                       - Clear all contacts."""

# Function to add a new contact
@input_error
def add_contact(command):
    parts = command.split(" ")
    if len(parts) >= 3:
        name, phone = parts[1], parts[2]
        name_field = Name(name)
        phone_field = Phone(phone)
        record = Record(name=name_field.value)
       

        if len(parts) >= 4:
            birthday = parts[3]
            birthday_field = Birthday(birthday)
            record.birthday = birthday_field

        record.add_phone(phone_field.value)
        address_book.add_record(record)

        if record.birthday:
            result = f"Contact {name} with number {phone} and birthday {record.birthday} saved."
        else:
            result = f"Contact {name} with number {phone} saved."

        return result
    else:
        raise ValueError("Invalid command format. Please enter name and phone.")

# Function to change the phone number of an existing contact
@input_error
def change_contact(command):
    parts = command.split(" ")
    if len(parts) == 4:
        name, old_phone, new_phone = parts[1], parts[2], parts[3]
        record = address_book.find(name)
        if record:
            new_phone_field = Phone(new_phone)
            result = record.edit_phone(old_phone, new_phone_field.value)
            return result
        else:
            raise KeyError(f"Contact {name} not found")
    else:
        raise ValueError("Invalid command format. Please enter name old phone and new phone.")

# Function to output the phone number of a contact
@input_error
def get_phone(command):
    parts = command.split(" ")
    if len(parts) == 2:
        name = parts[1]
        record = address_book.find(name)
        if record:
            phones_info = ', '.join(phone.value for phone in record.phones)
            return f"Phone numbers for {name}: {phones_info}"
        else:
            raise KeyError
    else:
        raise ValueError
    
# Display contacts with pagination  
@input_error 
def display_contacts_pagination(records, items_per_page=3):
    total_pages = (len(records) + items_per_page - 1) // items_per_page

    page = 1
    while True:
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        current_records = records[start_index:end_index]

        if not current_records:
            print("Contact list is empty")
            break

        result = f"Page {page}/{total_pages}:\n"
        for record in current_records:
            phones_info = ', '.join(phone.value for phone in record.phones)
            result += f"{record.name.value}:\n  Phone numbers: {phones_info}\n  Birthday: {record.birthday}\n"

        print(result)

        user_input = input("Type 'next' to view the next page, 'prev' for the previous page, or 'exit' to quit: ").strip().lower()

        if user_input == 'next' and page < total_pages:
            page += 1
        elif user_input == 'prev' and page > 1:
            page -= 1
        elif user_input == 'exit':
            break
        else:
            print("Invalid command. Please enter 'next', 'prev', or 'exit'.")

    return "Showing contacts completed."

# Function to display all contacts
@input_error
def show_all_contacts():
    records = address_book.data.values()
    if records:
        result = "All contacts:\n"
        for record in records:
            phones_info = ', '.join(phone.value for phone in record.phones)
            result += f"{record.name.value}:\n  Phone numbers: {phones_info}\n  Birthday: {record.birthday}\n"
        return result
    else:
        return "Contact list is empty"

# Function to terminate the bot
def exit_bot():
    return "Good bye!"

# Function to handle unknown commands
@input_error
def unknown_command(command):
    return f"Unknown command: {command}. Type 'help' for available commands."

# Function to save the address book to disk
@input_error
def save_to_disk():
    filename = input("Enter the filename to save the address book: ").strip()
    address_book.save_to_disk(filename)
    return f"Address book saved to {filename}"

# # Function to load the address book from disk
@input_error
def load_from_disk():
    filename = input("Enter the filename to load/create the address book: : ").strip()
    address_book.load_from_disk(filename)
    return f"Address book loaded from {filename}"

# Function to search for contacts
@input_error
def search_contacts():
    query = input("Enter the search query: ").strip()
    results = address_book.search_contacts(query)

    if results:
        print(f"Search results for '{query}':")
        for result in results:
            phones_info = ', '.join(phone.value for phone in result.phones)
            birthday_info = result.birthday if result.birthday else "None"
            print(f"Contact name: {result.name.value}\n  Phones: {phones_info}\n  Birthday: {birthday_info}")
    else:
        print(f"No results found for '{query}'.")

# Function to show the number of days to birthday
@input_error
def when_birthday(command):
    parts = command.split(" ")
    if len(parts) == 2:
        name = parts[1]
        record = address_book.find(name)
        if record:
            return f"Days until birthday for {name}: {record.days_to_birthday()} days."
        else:
            raise KeyError
    else:
        raise ValueError

# Function for updating birthday  
@input_error
def update_birthday(command):
    parts = command.split(" ")
    if len(parts) == 3:
        name, new_birthday = parts[1], parts[2]
        record = address_book.find(name)
        if record:
            record.update_birthday(new_birthday)
            return f"Birthday for {name} updated to {new_birthday}."
        else:
            raise KeyError(f"Contact {name} not found")
    else:
        raise ValueError("Invalid command format. Please enter old_birthday name new_birthday.")
    
# Function to remove a phone from an existing contact
@input_error
def remove_phone_from_contact(command):
    parts = command.split(" ")
    if len(parts) == 3:
        name, phone = parts[1], parts[2]
        record = address_book.find(name)
        if record:
            result = record.remove_phone(phone)
            return result
        else:
            raise KeyError
    else:
        raise ValueError
    
# Function to delete an entire contact
@input_error
def delete_contact(command):
    parts = command.split(" ")
    if len(parts) == 2:
        name = parts[1]
        try:
            address_book.delete(name)
            return f"Contact {name} deleted."
        except KeyError:
            return f"Contact {name} not found."
    else:
        raise ValueError("Invalid command format for deleting a contact.")
    
# Parse and execute the user command
def main():

    while True:
        command = input("\nEnter command: ").lower().strip()

        if command == "hello":
            print(hello())
        elif command == "help":
            print(help())
        elif command.startswith("add "):
            print(add_contact(command))
        elif command.startswith("change "):
            print(change_contact(command))
        elif command.startswith("phone "):
            print(get_phone(command))
        elif command.startswith("when "):
            print(when_birthday(command))
        elif command.startswith("birthday "):
            print(update_birthday(command))
        elif command == "show all":
            display_contacts_pagination(list(address_book.data.values()), items_per_page=3)
        elif command == "save":
            save_to_disk()
        elif command == "load":
            load_from_disk()
        elif command == "search":
            search_contacts()
        elif command.startswith("delete "):
            print(delete_contact(command))
        elif command.startswith("remove "):
            print(remove_phone_from_contact(command))
        elif command == "clear all":
            address_book.clear_all_contacts()
        elif command in ["good bye", "close", "exit"]:
            save_to_disk()
            print("Good bye!")
            break
        else:
            print(unknown_command(command))
            
if __name__ == "__main__":
    load_from_disk()
    main()

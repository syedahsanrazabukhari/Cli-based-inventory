from datetime import datetime
import json
from abc import ABC, abstractmethod


class Item(ABC):
    def __init__(self, id_, name, price, quantity):
        self.id = id_
        self.name = name
        self.price = price
        self.quantity = quantity

    def restock(self, amount):
        self.quantity += amount

    def sell(self, amount):
        if amount > self.quantity:
            raise ValueError("Insufficient stock.")
        self.quantity -= amount

    def stock_value(self):
        return self.price * self.quantity

    @abstractmethod
    def describe(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass


class Electronic(Item):
    def __init__(self, id_, name, price, quantity, brand, warranty):
        super().__init__(id_, name, price, quantity)
        self.brand = brand
        self.warranty = warranty

    def describe(self):
        return f"[Electronics] {self.name} | Brand: {self.brand} | Warranty: {self.warranty}yrs | Price: ${self.price} | Stock: {self.quantity}"

    def to_dict(self):
        return {
            "type": "Electronic",
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "brand": self.brand,
            "warranty": self.warranty
        }


class Food(Item):
    def __init__(self, id_, name, price, quantity, expiry):
        super().__init__(id_, name, price, quantity)
        self.expiry = expiry

    def is_expired(self):
        return datetime.strptime(self.expiry, "%Y-%m-%d").date() < datetime.now().date()

    def describe(self):
        status = "Expired" if self.is_expired() else "Fresh"
        return f"[Food] {self.name} | Expiry: {self.expiry} ({status}) | Price: ${self.price} | Stock: {self.quantity}"

    def to_dict(self):
        return {
            "type": "Food",
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "expiry": self.expiry
        }


class Apparel(Item):
    def __init__(self, id_, name, price, quantity, size, fabric):
        super().__init__(id_, name, price, quantity)
        self.size = size
        self.fabric = fabric

    def describe(self):
        return f"[Apparel] {self.name} | Size: {self.size} | Fabric: {self.fabric} | Price: ${self.price} | Stock: {self.quantity}"

    def to_dict(self):
        return {
            "type": "Apparel",
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "size": self.size,
            "fabric": self.fabric
        }


class Inventory:
    def __init__(self, filename="my-inventery.json"):
        self.items = {}
        self.filename = filename
        self.load_from_file()

    def save_to_file(self):
        with open(self.filename, "w") as f:
            json.dump([v.to_dict() for v in self.items.values()], f, indent=2)

    def load_from_file(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                for d in data:
                    if d["type"] == "Electronic":
                        item = Electronic(d["id"], d["name"], d["price"], d["quantity"], d["brand"], d["warranty"])
                    elif d["type"] == "Food":
                        item = Food(d["id"], d["name"], d["price"], d["quantity"], d["expiry"])
                    elif d["type"] == "Apparel":
                        item = Apparel(d["id"], d["name"], d["price"], d["quantity"], d["size"], d["fabric"])
                    else:
                        continue
                    self.items[d["id"]] = item
        except (FileNotFoundError, json.JSONDecodeError):
            self.items = {}

    def add_item(self, item):
        if item.id in self.items:
            raise ValueError("Item ID already exists.")
        self.items[item.id] = item
        self.save_to_file()

    def sell_item(self, id_, qty):
        if id_ in self.items:
            self.items[id_].sell(qty)
            self.save_to_file()

    def remove_expired(self):
        self.items = {k: v for k, v in self.items.items() if not (isinstance(v, Food) and v.is_expired())}
        self.save_to_file()

    def total_value(self):
        return sum(i.stock_value() for i in self.items.values())

    def search_by_name(self, term):
        return [v.describe() for v in self.items.values() if term.lower() in v.name.lower()]

    def list_all(self):
        return [v.describe() for v in self.items.values()]


def main():
    inv = Inventory()
    while True:
        print("\n📦 Inventory Manager")
        print("1. Add item")
        print("2. Sell item")
        print("3. View all items")
        print("4. Search by name")
        print("5. Remove expired food")
        print("6. View total value")
        print("0. Exit")
        option = input("Choose an option: ")

        try:
            if option == "1":
                type_ = input("Type (Electronic / Food / Apparel): ").lower()
                id_ = input("ID: ")
                name = input("Name: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))
                if type_ == "electronic":
                    brand = input("Brand: ")
                    warranty = int(input("Warranty (years): "))
                    item = Electronic(id_, name, price, qty, brand, warranty)
                elif type_ == "food":
                    expiry = input("Expiry (YYYY-MM-DD): ")
                    item = Food(id_, name, price, qty, expiry)
                elif type_ == "apparel":
                    size = input("Size: ")
                    fabric = input("Fabric: ")
                    item = Apparel(id_, name, price, qty, size, fabric)
                else:
                    print("Invalid type.")
                    continue
                inv.add_item(item)
                print("✅ Item added and saved.")
            elif option == "2":
                id_ = input("Item ID: ")
                qty = int(input("Quantity: "))
                inv.sell_item(id_, qty)
                print("✅ Item sold and inventory updated.")
            elif option == "3":
                for item in inv.list_all():
                    print(item)
            elif option == "4":
                term = input("Search term: ")
                results = inv.search_by_name(term)
                for r in results:
                    print(r)
            elif option == "5":
                inv.remove_expired()
                print("✅ Expired food removed.")
            elif option == "6":
                print(f"💰 Total stock value: ${inv.total_value():.2f}")
            elif option == "0":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice.")
        except Exception as e:
            print("⚠️ Error:", e)


if __name__ == "__main__":
    main()

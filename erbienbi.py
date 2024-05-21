import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QListWidget, QDateEdit, QComboBox
)
from PyQt5.QtCore import QDate
from abc import ABC, abstractmethod
from datetime import date, datetime


class Room(ABC):
    def __init__(self, price, room_number):
        self._price = price
        self._room_number = room_number

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def room_number(self):
        return self._room_number

    @room_number.setter
    def room_number(self, value):
        self._room_number = value

    @abstractmethod
    def get_price(self):
        pass


class SingleRoom(Room):
    def __init__(self, price, room_number):
        super().__init__(price, room_number)

    def get_price(self):
        return self.price


class DoubleRoom(Room):
    def __init__(self, price, room_number):
        super().__init__(price, room_number)

    def get_price(self):
        return self.price


class Hotel:
    def __init__(self, name):
        self._name = name
        self._rooms = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def rooms(self):
        return self._rooms

    def add_room(self, room):
        self._rooms.append(room)


class Reservation:
    def __init__(self, room, date):
        self._room = room
        self._date = date

    @property
    def room(self):
        return self._room

    @property
    def date(self):
        return self._date


class HotelBooking:
    def __init__(self, hotel):
        self._hotel = hotel
        self._reservations = []

    @property
    def hotel(self):
        return self._hotel

    @property
    def reservations(self):
        return self._reservations

    def book_room(self, room_type, date):
        available_room = self.get_available_room(room_type, date)
        if available_room:
            reservation = Reservation(available_room, date)
            self._reservations.append(reservation)
            return available_room.get_price()
        return None

    def cancel_reservation(self, room_type, room_number, date):
        for reservation in self._reservations:
            print("Checking reservation: Room", reservation.room.room_number, "Date:", reservation.date)
            if isinstance(reservation.room, room_type) and str(
                    reservation.room.room_number) == room_number and reservation.date == date:
                self._reservations.remove(reservation)
                print("Reservation cancelled:", room_number, date)
                print("Reservations after cancellation:",
                      [(reservation.room.room_number, reservation.date) for reservation in self._reservations])
                return True

        print("No booking found for the given room number, room type, and date.")
        return False

    def list_reservations(self):
        return self._reservations

    def is_valid_date(self, date):
        return date > datetime.now().date()

    def get_available_room(self, room_type, date):
        for room in self._hotel.rooms:
            if isinstance(room, room_type) and self.is_room_available(room, date):
                return room
        return None

    def is_room_available(self, room, date):
        for reservation in self._reservations:
            if reservation.room.room_number == room.room_number and reservation.date == date:
                return False
        return True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.hotel = Hotel("GDE Hotel")
        self.hotel.add_room(SingleRoom(5000, 101))
        self.hotel.add_room(SingleRoom(5000, 102))
        self.hotel.add_room(DoubleRoom(8000, 201))

        self.hotel_booking = HotelBooking(self.hotel)

        # Adding initial reservations
        initial_reservations = [
            (SingleRoom, QDate(2024, 6, 1).toPyDate()),
            (SingleRoom, QDate(2024, 6, 2).toPyDate()),
            (SingleRoom, QDate(2024, 6, 1).toPyDate()),
            (DoubleRoom, QDate(2024, 6, 3).toPyDate()),
            (DoubleRoom, QDate(2024, 6, 4).toPyDate())
        ]

        for room_type, date in initial_reservations:
            self.hotel_booking.book_room(room_type, date)

        self.setWindowTitle("ErBíEnBí")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        # Booking section
        self.booking_layout = QVBoxLayout()
        self.layout.addLayout(self.booking_layout)

        self.booking_label = QLabel("Foglalás")
        self.booking_layout.addWidget(self.booking_label)

        self.room_type_input = QComboBox()
        self.room_type_input.addItem("Egyágyas szoba")
        self.room_type_input.addItem("Franciaágyas szoba")
        self.booking_layout.addWidget(self.room_type_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setMinimumDate(QDate.currentDate().addDays(1))
        self.booking_layout.addWidget(self.date_input)

        self.book_button = QPushButton("Foglalom")
        self.book_button.clicked.connect(self.create_booking)
        self.booking_layout.addWidget(self.book_button)

        # Cancellation section
        self.cancellation_layout = QVBoxLayout()
        self.layout.addLayout(self.cancellation_layout)

        self.cancellation_label = QLabel("Foglalás törlése")
        self.cancellation_layout.addWidget(self.cancellation_label)

        self.cancel_room_number_input = QLineEdit()
        self.cancel_room_number_input.setPlaceholderText("Szobaszám")
        self.cancellation_layout.addWidget(self.cancel_room_number_input)

        self.cancel_date_input = QDateEdit()
        self.cancel_date_input.setCalendarPopup(True)
        self.cancel_date_input.setMinimumDate(QDate.currentDate())
        self.cancellation_layout.addWidget(self.cancel_date_input)

        self.cancel_button = QPushButton("Lemondom")
        self.cancel_button.clicked.connect(self.cancel_booking)
        self.cancellation_layout.addWidget(self.cancel_button)

        # Listing section
        self.listing_layout = QVBoxLayout()
        self.layout.addLayout(self.listing_layout)

        self.listing_label = QLabel("Foglalások listázása")
        self.listing_layout.addWidget(self.listing_label)

        self.list_button = QPushButton("Nézzük")
        self.list_button.clicked.connect(self.list_bookings)
        self.listing_layout.addWidget(self.list_button)

        self.booking_list = QListWidget()
        self.listing_layout.addWidget(self.booking_list)

        # Central widget setup
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def create_booking(self):
        room_type_text = self.room_type_input.currentText()
        room_type = SingleRoom if room_type_text == "Egyágyas szoba" else DoubleRoom
        date = self.date_input.date().toPyDate()

        price = self.hotel_booking.book_room(room_type, date)
        if price:
            QMessageBox.information(self, "Sikeres foglalás!", f"Sikeres foglalás! Ára: {price} Ft")
        else:
            QMessageBox.warning(self, "Hiba", "Nem elérhető szoba a megadott dátumon.")

    def cancel_booking(self):
        room_number = self.cancel_room_number_input.text()
        date = self.cancel_date_input.date().toPyDate()

        if not room_number:
            QMessageBox.warning(self, "Hiba", "Kérlek, add meg a szobaszámot!")
            return

        room_type_text = self.room_type_input.currentText()
        room_type = SingleRoom if room_type_text == "Egyágyas szoba" else DoubleRoom

        print("Cancelling reservation for room type:", room_type_text)
        print("Room number entered for cancellation:", room_number)
        print("Date:", date)

        if self.hotel_booking.cancel_reservation(room_type, room_number, date):
            QMessageBox.information(self, "Lemondás sikeres.", "A foglalásod töröltük.")
        else:
            QMessageBox.warning(self, "Hiba", "Nem találjuk a foglalásod.")

    def list_bookings(self):
        self.booking_list.clear()
        for reservation in self.hotel_booking.list_reservations():
            self.booking_list.addItem(f"Room: {reservation.room.room_number}, Date: {reservation.date}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

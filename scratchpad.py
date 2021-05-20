class Car:

    def __init__(self, wheels, doors, hp, manufacturer):
        self.wheels = wheels
        self.doors = doors
        self.hp = hp
        self.manufacturer = manufacturer

    def apply_break(self):
        print('Braking')


Outback = Car(4, 4, 200, 'Subaru')


Civic = Car(2,4,15,'Honda')

Civic, Outback

class Road:

    def __init__(self, cars):
        self.cars = cars

road = Road([Outback, Civic])

if Outback.manufacturer == 'Subaru':
    Outback.apply_break()
else:
    Civic.apply_break()

Outback.doors = 2
print(Outback.doors)

print("Hello World!")
my_tuple = (1,2,3,2,1)
print(my_tuple)
my_tuple = (1, "apple", 2, "banana")
print(my_tuple[3])
my_set = {1,2,3,4,5,6,4,5,6,1}
print(my_set)
my_dict = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}
print(my_dict["name"])  
print(10 < 10)
print(10 <= 10)
age = int(input("Enter your age:"))
if age >= 18:
    print("Adult")
else: 
    print("Under age")
    numbers = [1,2,3]
    for n in numbers:
          print(n)
    for letter in "hello":
         print(letter)
    for i in range(5):
         print(i)
    x = 0 
    while x < 3:
         print(x)
    while True:
         print("Endlessly Working")
    for i in range(10):
         if i == 5:
              break
    print(i)

    while True:
         x = input("Put Stop")
         if x == "stop":
              break
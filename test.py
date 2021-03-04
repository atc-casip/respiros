class Test:
    def __init__(self):
        self.value = 10


if __name__ == "__main__":
    test = Test()
    if not test.another:
        test.another = 20

    print(test.value)
    print(test.another)

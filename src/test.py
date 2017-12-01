class test():
    def __init__(self):
        print('hej')

    def __getitem__(self, item):
        return 'jeeeej!'

if __name__ == "__main__":
    x = test()
    print(x['test'])
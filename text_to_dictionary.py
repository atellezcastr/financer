test_dict = dict(0:'MakeAChoice')
with open("./toi.txt", "r") as f:
    for idx, line in enumerate(f.readlines(),1):
        test_dict[idx] = line.strip()

print(test_dict)

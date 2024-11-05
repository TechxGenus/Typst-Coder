import json
import random
random.seed(0)

with open("typst.json", "r") as f:
    data = json.load(f)

data = [{k: v for k, v in item.items() if k != 'id'} for item in data]

random.shuffle(data)

test_data = data[:1000]
train_data = data[1000:]

with open("typst_train.json", "w") as train_file:
    json.dump(train_data, train_file, indent=4)

with open("typst_test.json", "w") as test_file:
    json.dump(test_data, test_file, indent=4)

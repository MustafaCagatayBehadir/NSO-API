import yaml

with open("data.yaml", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

print(data)
print("\n----------YAML Serialized Format------------\n")
print(yaml.dump(data))
import yaml

data = {
    "Name": "John Doe",
    "Age": 40,
    "Company": "XYZ",
    "Social-media": {"Facebook": "johndoe",
                     "twitter": "johndoe"},
    "Job Title": "Network Automation Engineer",
    "Skills": ["Python", "Nexus", "IOS-XE", "YAML", "JSON"]
}

print(yaml.dump(data))

with open("test.yaml", "w") as f:
    yaml.dump(data, f)
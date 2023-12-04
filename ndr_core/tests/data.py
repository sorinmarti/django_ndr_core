""" Test data for ndr_core tests. """

TEST_DATA = {
        "test_value": "cat",
        "test_list": [
            "fish",
            "dog",
            "guinea pig"
        ],
        "nested_data": {
            "nested_value": "lion",
            "nested_list": [
                "gazelle",
                "zebra",
                "buffalo"
            ]
        },
        "nested_list": [
            {
                "nested_list_value1": "work horses",
                "nested_list_value2": "work dogs",
                "nested_list_value3": "work bulls"
            },
            {
                "nested_list_value1": "nested_list_value1",
                "nested_list_value2": "nested_list_value2",
                "nested_list_value3": "nested_list_value3"
            },
            {
                "nested_list_value1": "nested_list_value1",
                "nested_list_value2": "nested_list_value2",
                "nested_list_value3": "nested_list_value3"
            }
        ],
        "another_test_list": [
            {
                "key_1": "value_1",
                "key_2": "value_2",
            },
            {
                "key_1": "value_1",
                "key_2": "value_2",
            },
            {
                "key_1": "value_1",
                "key_2": "value_2",
            }
        ],
        "tags": [
            {"key": "cat", "id": "a3248fgnvcjhd9"},
            {"key": "dog", "id": "a3248fgnvcjhd9"},
            {"key": "fish", "id": "a3248fgnvcjhd9"},
            {"key": "guinea pig", "id": "a3248fgnvcjhd9"},
            {"key": "lion", "id": "a3248fgnvcjhd9"},
            {"key": "gazelle", "id": "a3248fgnvcjhd9"},
            {"key": "zebra", "id": "a3248fgnvcjhd9"},
            {"key": "buffalo", "id": "a3248fgnvcjhd9"},
            {"key": "work horses", "id": "a3248fgnvcjhd9"},
        ]
    }

LIST_CHOICES = """key,value,value_de,info,info_de
cat,Cat,Katze,A cat is a feline.,Eine Katze ist ein Feline.
dog,Dog,Hund,A dog is a canine.,Ein Hund ist ein Canine.
fish,Fish,Fisch,A fish is a fish.,Ein Fisch ist ein Fisch.
guinea pig,Guinea pig,Meerschweinchen,A guinea pig is a rodent.,Ein Meerschweinchen ist ein Nagetier.
lion,Lion,Löwe,A lion is a feline.,Ein Löwe ist ein Feline.
gazelle,Gazelle,Gazelle,A gazelle is a mammal.,Eine Gazelle ist ein Säugetier.
zebra,Zebra,Zebra,A zebra is a mammal.,Ein Zebra ist ein Säugetier.
buffalo,Buffalo,Büffel,A buffalo is a mammal.,Ein Büffel ist ein Säugetier.
work horses,Work horses,Arbeitspferde,Work horses are horses that work.,"Arbeitspferde sind Pferde, die arbeiten." 
"""
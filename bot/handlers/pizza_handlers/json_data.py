import json

pizza_names_list = ['Pepperoni', 'Pepperoni Fresh',  'Diablo', 'Original']
select_pizza = json.dumps({
    "inline_keyboard": [[{'text': name, 'callback_data': 'pizza_' + name.lower()}
            for name in pizza_names_list[names: (names + 2)]]
            for names in range(0, len(pizza_names_list), 2)
    ]
})


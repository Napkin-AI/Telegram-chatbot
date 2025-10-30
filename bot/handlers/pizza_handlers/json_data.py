import json

pizza_names_list = ['Pepperoni', 'Pepperoni Fresh',  'Diablo', 'Original']
pizza_size_list = ['Small (25cm)', 'Medium (30cm)', 'Large (35cm)', 'Double (50cm)']
drinks_list = ['Tea', 'Coffee', 'Water', 'No drinks']

select_pizza = json.dumps({
    "inline_keyboard": [[{'text': name, 'callback_data': 'pizza_' + name.lower()}
            for name in pizza_names_list[names: (names + 2)]]
            for names in range(0, len(pizza_names_list), 2)
    ]
})

select_size = json.dumps({
    "inline_keyboard": [[{'text': name, 'callback_data': 'size_' + name.lower()}
            for name in pizza_size_list[names: (names + 2)]]
            for names in range(0, len(pizza_size_list), 2)
    ]
})

select_drinks = json.dumps({
    "inline_keyboard": [[{'text': name, 'callback_data': 'drink_' + name.lower()}
            for name in drinks_list[names: (names + 2)]]
            for names in range(0, len(drinks_list), 2)
    ]
})

approve_json = json.dumps({
    "inline_keyboard": [
        [
            {'text': 'Approve', 'callback_data': 'approve_ok'},
            {'text': 'Change order', 'callback_data': 'approve_restore'}
        ]
    ]
})
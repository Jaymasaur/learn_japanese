import json
import os

def load_data(type_, data_dir):
    filename = {
        'Hiragana': 'hiragana.json',
        'Katakana': 'katakana.json',
        'Conversation': 'conversation.json'
    }.get(type_)
    if not filename:
        return []
    path = os.path.join(data_dir, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def get_end_options(type_, data):
    if not data:
        return []
    if type_ == 'Conversation':
        return [str(item['id']) for item in data]
    else:
        # Only show unique rowStart values, and display the first item's 'english' for each row
        seen = set()
        options = []
        for item in data:
            rs = item.get('rowStart')
            if rs and rs not in seen:
                options.append({'value': rs, 'label': item['english']})
                seen.add(rs)
        return options

def filter_practice_items(type_, data, end_at, row_mode='upto'):
    if not data:
        return []

    if type_ == 'Conversation':
        end_id = int(end_at)
        return [item for item in data if int(item['id']) <= end_id]

    if type_ in ['Hiragana', 'Katakana']:
        if not end_at:
            return data
        # Convert end_at to int for comparison
        try:
            end_at_int = int(end_at)
        except Exception:
            end_at_int = end_at

        row_starts = [item['rowStart'] for item in data if 'rowStart' in item]
        if end_at_int not in row_starts:
            return data

        if row_mode == 'single':
            # Only include items with the selected rowStart value
            return [item for item in data if item.get('rowStart') == end_at_int]
        else:
            # Include all items with rowStart <= selected row value
            return [item for item in data if item.get('rowStart') is not None and item.get('rowStart') <= end_at_int]

    return data

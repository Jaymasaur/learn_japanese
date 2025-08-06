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
                options.append(item['english'])
                seen.add(rs)
        return options

def filter_practice_items(type_, data, end_at):
    if not data:
        return []
    if type_ == 'Conversation':
        end_id = int(end_at)
        return [item for item in data if int(item['id']) <= end_id]
    else:
        # Find the rowStart for the selected end_at (which is the 'english' value)
        end_rowStart = None
        for item in data:
            if item['english'] == end_at:
                end_rowStart = item['rowStart']
                break
        if end_rowStart is None:
            return []
        # Collect all items with rowStart <= end_rowStart
        return [item for item in data if item['rowStart'] <= end_rowStart]

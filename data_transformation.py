import glob
import json

def transform_data(data):
    unique_files = {
        'masterCategory': './resources/clean/categories.json',
        'subCategory': './resources/clean/subcategories.json',
        'articleType': './resources/clean/articletypes.json'
    }

    unique_items = {}
    for key, path in unique_files.items():
        if glob.glob(path):
            with open(path, 'r', encoding='utf8') as f:
                unique_items[key] = {item['id']: item for item in json.load(f)}
        else:
            unique_items[key] = {}

    transformed_data = []
    for item in data:
        new_item = {}
        data_object = item['data']

        if 'kid' in data_object['ageGroup'].lower():
            continue

        new_item['id'] = data_object.get('id')
        new_item['price'] = data_object.get('price')
        new_item['discountedPrice'] = data_object.get('discountedPrice')
        new_item['articleNumber'] = data_object.get('articleNumber')
        new_item['productDisplayName'] = data_object.get('productDisplayName')
        new_item['brandName'] = data_object.get('brandName')
        new_item['gender'] = data_object.get('gender')
        new_item['baseColour'] = data_object.get('baseColour')
        new_item['season'] = data_object.get('season')
        new_item['usage'] = data_object.get('usage')
        new_item['Pattern'] = data_object.get('articleAttributes', {}).get('Pattern')
        new_item['defaultImageURL'] = data_object.get('styleImages', {}).get('default', {}).get('imageURL')
        new_item['backImageURL'] = data_object.get('styleImages', {}).get('back', {}).get('imageURL')
        new_item['frontImageURL'] = data_object.get('styleImages', {}).get('front', {}).get('imageURL')
        new_item['productDescriptors'] = data_object.get('productDescriptors')

        for key in ['masterCategory', 'subCategory', 'articleType']:
            id_val = data_object.get(key, {}).get('id')
            name_val = data_object.get(key, {}).get('typeName')
            new_item[key+'Id'] = id_val
            if id_val not in unique_items[key]:
                unique_items[key][id_val] = {"id": id_val, "typeName": name_val}
                with open(unique_files[key], 'w', encoding='utf8') as f:
                    json.dump(list(unique_items[key].values()), f)

        if 'styleOptions' in data_object:
            for index, option in enumerate(data_object['styleOptions']):
                new_item[f'size_{index}'] = option.get('value')
        
        transformed_data.append(new_item)

    return transformed_data
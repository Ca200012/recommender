import glob
import json
import os
from collections import defaultdict

def find_dict(dict_list, target_key, target_value):
    for dict_item in dict_list:
        if dict_item.get(target_key) == target_value:
            return dict_item
    return None

def transform_data(data):
    
    # Check if file exists and delete it
    article_file_path = './resources/clean/articles.json'
    if os.path.isfile(article_file_path):
        os.remove(article_file_path)

    structure_file_path = './resources/clean/structure.json'
    if os.path.isfile(structure_file_path):
        os.remove(structure_file_path)

    transformed_data = []
    structure = {"gender": []}

    for item in data:
        new_item = {}
        data_object = item['data']

        # eliminam articolele de copii
        if 'kid' in data_object['ageGroup'].lower():
            continue

        # eliminam articolele care au alte marimi fata de cele mentionate
        invalid_size_flag = False
        if 'styleOptions' in data_object:
            for index, option in enumerate(data_object['styleOptions']):
                size_value = option.get('value')
                if size_value not in ['S', 'M', 'L', 'XL', 'XXL']:
                    invalid_size_flag = True
                    break
                new_item[f'size_{index}'] = size_value

        if invalid_size_flag:
            continue

        # prepare the structure
        gender = data_object['gender']

        # declare category structure
        category = {
            "id": data_object['masterCategory']['id'],
            "name": data_object['masterCategory']['typeName'],
            "subCategories": []
        }

        # declare subCategory structure 
        subCategory = {
            "id": data_object['subCategory']['id'],
            "name": data_object['subCategory']['typeName'],
            "articleTypes": []
        }

        # declare articleType structure 
        articleType = {
            "id": data_object['articleType']['id'],
            "name": data_object['articleType']['typeName']
        }

        # If gender does not exist, create it
        gender_dict = next((g for g in structure['gender'] if list(g.keys())[0] == gender), None)
        if gender_dict is None:
            gender_dict = {gender: {"categories": []}}
            structure['gender'].append(gender_dict)

        # Find or create category
        category_dict = find_dict(gender_dict[gender]["categories"], "id", category["id"])
        if category_dict is None:
            gender_dict[gender]["categories"].append(category)
            category_dict = category

        # Find or create subCategory
        sub_category_dict = find_dict(category_dict["subCategories"], "id", subCategory["id"])
        if sub_category_dict is None:
            category_dict["subCategories"].append(subCategory)
            sub_category_dict = subCategory

        # Find or create articleType
        article_type_dict = find_dict(sub_category_dict["articleTypes"], "id", articleType["id"])
        if article_type_dict is None:
            sub_category_dict["articleTypes"].append(articleType)

        # prepare simple keys and values
        keys = ['id', 'price', 'discountedPrice', 'articleNumber', 'productDisplayName', 'brandName', 'gender', 'baseColour', 'season', 'usage']

        for i in keys:
            new_item[i] = data_object.get(i)

        # prepare complex keys and values
        new_item['Pattern'] = data_object.get('articleAttributes', {}).get('Pattern')
        new_item['defaultImageURL'] = data_object.get('styleImages', {}).get('default', {}).get('imageURL')
        new_item['backImageURL'] = data_object.get('styleImages', {}).get('back', {}).get('imageURL')
        new_item['frontImageURL'] = data_object.get('styleImages', {}).get('front', {}).get('imageURL')
        new_item['description'] = data_object.get('productDescriptors', {}).get('description', {}).get('value')

        for key in ['masterCategory', 'subCategory', 'articleType']:
            id_val = data_object.get(key, {}).get('id')
            new_item[key+'Id'] = id_val
        
        transformed_data.append(new_item)

    # Write the structure to the output file
    with open('./resources/clean/structure.json', 'w') as f:
        json.dump(structure, f, indent=4)

    # Write the articles to the output file
    with open('./resources/clean/articles.json', 'w') as f:
        json.dump(transformed_data, f, indent=4)
    return transformed_data
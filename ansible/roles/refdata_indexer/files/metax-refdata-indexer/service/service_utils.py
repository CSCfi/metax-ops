from os.path import isfile

def set_default_label(label):
    if label and len(label) > 0:
        if 'fi' in label:
            label['und'] = label['fi']
        elif 'en' in label:
            label['und'] = label['en']
        else:
            label['und'] = next(iter(label.values()))


def file_exists(file_path):
    return isfile(file_path)
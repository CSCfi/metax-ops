def set_default_label(label):
    if label and len(label) > 0:
        if 'fi' in label:
            label['default'] = label['fi']
        elif 'en' in label:
            label['default'] = label['en']
        else:
            label['default'] = next(iter(label.values()))

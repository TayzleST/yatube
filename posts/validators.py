from django import forms


def validate_file_size(image):
    # устанавливаем максимальный размер для загружаемого на сайт файла
    filesize = image.size
    if filesize > 5242880:
        raise forms.ValidationError(
                message='Максимальный размер изображения не должен превышать 5 Мбайт',
                )
    else:
        return image
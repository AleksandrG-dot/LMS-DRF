from rest_framework import serializers


def validate_url_youtube(url: str) -> bool:
    """Валидатор проверяет на наличие в строке ссылки youtube.com"""
    if "youtube.com" not in url.lower():
        raise serializers.ValidationError(
            "Допустимы только ссылки на видео с youtube.com"
        )

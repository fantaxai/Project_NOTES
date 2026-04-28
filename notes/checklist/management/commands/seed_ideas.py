from django.core.management.base import BaseCommand

from checklist.models import Idea


class Command(BaseCommand):
    def handle(self, *args, **options):
        ideas_data = [
            # Учеба
            {"category": "study", "text": "Составить план подготовки к экзамену"},
            {"category": "study", "text": "Найти 3 статьи по теме курсовой"},
            {"category": "study", "text": "Сделать конспект по сложной теме"},
            {"category": "study", "text": "Подготовить презентацию для выступления"},
            {"category": "study", "text": "Найти научного руководителя для исследования"},
            # Путешествия
            {"category": "travel", "text": "Составить маршрут выходного дня"},
            {"category": "travel", "text": "Найти интересные места в своём городе"},
            {"category": "travel", "text": "Спланировать бюджет поездки"},
            {"category": "travel", "text": "Собрать список must-see мест"},
            {"category": "travel", "text": "Изучить местную кухню перед поездкой"},
            # Искусство
            {"category": "art", "text": "Нарисовать скетч дня"},
            {"category": "art", "text": "Сходить на выставку или в музей"},
            {"category": "art", "text": "Написать короткий рассказ"},
            {"category": "art", "text": "Сделать коллаж из журналов"},
            {"category": "art", "text": "Научиться новому творческому приёму"},
            # Друзья
            {"category": "friends", "text": "Организовать встречу с друзьями"},
            {"category": "friends", "text": "Придумать идею для совместного досуга"},
            {"category": "friends", "text": "Сделать сюрприз для друга"},
            {"category": "friends", "text": "Написать письмо/открытку другу"},
            {"category": "friends", "text": "Создать общий плейлист"},
            # Семья
            {"category": "family", "text": "Позвонить родителям"},
            {"category": "family", "text": "Придумать активность для всей семьи"},
            {"category": "family", "text": "Создать семейный фотоальбом"},
            {"category": "family", "text": "Приготовить семейный рецепт"},
            {"category": "family", "text": "Написать историю семьи"},
            # Спорт
            {"category": "sport", "text": "Найти новый вид спорта для проб"},
            {"category": "sport", "text": "Составить план тренировок на неделю"},
            {"category": "sport", "text": "Сходить на утреннюю пробежку"},
            {"category": "sport", "text": "Попробовать йогу или медитацию"},
            {"category": "sport", "text": "Записаться на групповое занятие"},
            # Работа
            {"category": "work", "text": "Оптимизировать рабочий процесс"},
            {"category": "work", "text": "Освоить новый инструмент/программу"},
            {"category": "work", "text": "Провести анализ своих задач"},
            {"category": "work", "text": "Написать пост о своей работе"},
            {"category": "work", "text": "Найти наставника или стать им"},
            # Саморазвитие
            {"category": "self_development", "text": "Прочитать книгу по интересной теме"},
            {"category": "self_development", "text": "Пройти онлайн-курс"},
            {"category": "self_development", "text": "Освоить новый навык"},
            {"category": "self_development", "text": "Вести дневник благодарности"},
            {"category": "self_development", "text": "Поставить цель на месяц"},
        ]

        for data in ideas_data:
            idea, created = Idea.objects.get_or_create(category=data["category"], text=data["text"])
            if created:
                self.stdout.write(f"Создана идея: {idea}")

        self.stdout.write(self.style.SUCCESS(f"Добавлено {len(ideas_data)} идей"))

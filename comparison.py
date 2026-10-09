from typing import Dict, List, Any
from database.db_manager import ProgramManager

class ComparisonManager:
    def __init__(self):
        self.selected_programs = {}

    def add_program(self, level: str, program_id: int, program_manager: ProgramManager) -> None:
        """Добавляет программу в список для сравнения."""
        if level not in self.selected_programs:
            self.selected_programs[level] = {}
        if program_id not in self.selected_programs[level]:
            program_data = program_manager.select_one(program_id)
            if program_data:
                self.selected_programs[level][program_id] = program_data

    def remove_program(self, level: str, program_id: int) -> None:
        """Удаляет программу из списка для сравнения."""
        if level in self.selected_programs and program_id in self.selected_programs[level]:
            del self.selected_programs[level][program_id]
            if not self.selected_programs[level]:
                del self.selected_programs[level]

    def get_selected_programs(self, level: str) -> Dict[int, Dict[str, Any]]:
        """Возвращает список выбранных программ для указанного уровня."""
        return self.selected_programs.get(level, {})

    def compare_programs(self, level: str, program_manager: ProgramManager) -> List[Dict[str, Any]]:
        """Сравнивает выбранные программы по указанным параметрам."""
        programs = self.get_selected_programs(level)
        if not programs:
            return []

        comparison_data = []
        for program_id, program in programs.items():
            # Получаем дополнительные данные через ProgramManager
            passing_score = program_manager.get_passing_score(program_id)
            subjects = program_manager.get_subjects(program_id) if level == 'undergraduate' else []
            practice = program.get('practice', '-') if level == 'graduate' else '-'
            duration = program.get('study_duration', program.get('duration', '-'))
            form = program.get('form', '-')
            ege_sum = program.get('ege_sum', '-') if level == 'undergraduate' else '-'

            comparison_data.append({
                'id': program_id,
                'name': program['name'],
                'duration': duration,
                'subjects': subjects if subjects else ['-'],
                'passing_score': passing_score if passing_score else '-',
                'ege_sum': ege_sum,
                'form': form,
                'practice': practice
            })
        return comparison_data

    def get_detailed_info(self, level: str, program_id: int, program_manager: ProgramManager) -> Dict[str, Any]:
        """Возвращает расширенную информацию о программе."""
        program = program_manager.select_one(program_id)
        if not program:
            return {}

        passing_score = program_manager.get_passing_score(program_id)
        subjects = program_manager.get_subjects(program_id) if level == 'undergraduate' else []
        budget_places = program_manager.get_budget_places(program_id)
        practice = program.get('practice', '-') if level == 'graduate' else '-'
        duration = program.get('study_duration', program.get('duration', '-'))
        form = program.get('form', '-')
        ege_sum = program.get('ege_sum', '-') if level == 'undergraduate' else '-'

        return {
            'id': program_id,
            'name': program['name'],
            'duration': duration,
            'subjects': subjects if subjects else ['-'],
            'passing_score': passing_score if passing_score else '-',
            'ege_sum': ege_sum,
            'form': form,
            'practice': practice,
            'budget_places': budget_places if budget_places else '-',
            'description': program.get('description', 'Описание отсутствует')
        }